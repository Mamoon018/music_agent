"""
-----------------
Service layer for the "Create Account" endpoint.

Process flow:
    Request → Pydantic Validation → DB Duplicate Check → Hash Password → Store → Return Response

Dependencies:
    pip install pydantic bcrypt supabase structlog python-dotenv
"""

import uuid
import bcrypt
import structlog
from dataclasses import dataclass
from enum import Enum
from typing import Any

from pydantic import ValidationError
from supabase import create_client, Client

# Import the Pydantic model from users.py (same package / directory)
from src.models.users import UserCredentialsModel

# ---------------------------------------------------------------------------
# structlog configuration  (mirrors users.py — JSON lines, shared context)
# ---------------------------------------------------------------------------
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger().bind(service="create_account")

# ---------------------------------------------------------------------------
# Supabase client  (reads credentials from env — never hard-code secrets)
# ---------------------------------------------------------------------------
import os
from dotenv import load_dotenv

load_dotenv(".env.dev")                          # loads SUPABASE_URL and SUPABASE_KEY from .env
_SUPABASE_URL: str = os.environ["SUPABASE_URL"]
_SUPABASE_KEY: str = os.environ["SUPABASE_KEY"]

supabase: Client = create_client(_SUPABASE_URL, _SUPABASE_KEY)

USERS_TABLE = "users"

# ---------------------------------------------------------------------------
# Response shapes
# ---------------------------------------------------------------------------

class Status(str, Enum):
    SUCCESS = "success"
    ERROR   = "error"


@dataclass(frozen=True)
class ServiceResponse:
    """Unified response object returned to the caller (controller / endpoint)."""
    status:  Status
    message: str
    data:    dict | None = None
    errors:  list | None = None

    def to_dict(self) -> dict:
        return {
            "status":  self.status.value,
            "message": self.message,
            "data":    self.data,
            "errors":  self.errors,
        }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password with bcrypt (cost factor 12).
    Returns the hashed string safe for DB storage.
    """
    salt   = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def _check_duplicate(username: str, email: str) -> bool:
    """
    Return True if username OR email already exists in the users table.

    Two separate queries are issued intentionally so we hit the indexed
    columns individually — one combined OR filter can bypass partial indexes
    on some Supabase/Postgres configurations.

    We deliberately do NOT tell the caller *which* field matched to prevent
    user-enumeration attacks.
    """
    logger.info("Checking for duplicate credentials", step="duplicate_check")

    email_hit = (
        supabase
        .table(USERS_TABLE)
        .select("user_id")
        .eq("email", email)
        .limit(1)
        .execute()
    )
    if email_hit.data:
        logger.warning("Duplicate detected", matched_field="email_or_username")
        return True

    username_hit = (
        supabase
        .table(USERS_TABLE)
        .select("user_id")
        .eq("username", username)
        .limit(1)
        .execute()
    )
    if username_hit.data:
        logger.warning("Duplicate detected", matched_field="email_or_username")
        return True

    logger.info("No duplicate found", step="duplicate_check", status="ok")
    return False


def _insert_user(payload: dict) -> dict:
    """
    Insert a single user record into the users table and return the created row.
    Raises RuntimeError if Supabase does not return the inserted record.
    """
    logger.info("Inserting user record", step="db_insert")

    response = (
        supabase
        .table(USERS_TABLE)
        .insert(payload)
        .execute()
    )

    if not response.data:
        raise RuntimeError("Database insert returned no data — record may not have been created.")

    logger.info("User record inserted", step="db_insert", status="ok")
    return response.data[0]


# ---------------------------------------------------------------------------
# Public service function  (called by the FastAPI / Flask endpoint handler)
# ---------------------------------------------------------------------------

def create_account(raw_input: dict[str, Any]) -> ServiceResponse:
    """
    Orchestrates the full account-creation pipeline.

    Parameters
    ----------
    raw_input : dict
        Raw payload received from the API request body.
        Expected keys: username, password, email, full_name (optional).

    Returns
    -------
    ServiceResponse
        A frozen dataclass with status, message, optional data, and optional errors.
    """

    request_id = str(uuid.uuid4())
    log = logger.bind(request_id=request_id)

    log.info("create_account request received", step="start")

    # ------------------------------------------------------------------
    # STEP 1 — Pydantic validation
    # ------------------------------------------------------------------
    log.info("Running Pydantic validation", step="pydantic_validation")

    try:
        validated = UserCredentialsModel(**raw_input)
    except ValidationError as exc:
        # Collect ALL validation errors and return them together
        error_list = [
            {
                "field":   " → ".join(str(loc) for loc in err["loc"]) or "model",
                "message": err["msg"].replace("Value error, ", ""),
            }
            for err in exc.errors()
        ]
        log.warning(
            "Pydantic validation failed",
            step="pydantic_validation",
            status="failed",
            error_count=len(error_list),
        )
        return ServiceResponse(
            status=Status.ERROR,
            message="Validation failed. Please fix the errors and try again.",
            errors=error_list,
        )

    log.info("Pydantic validation passed", step="pydantic_validation", status="ok")

    # ------------------------------------------------------------------
    # STEP 2 — Duplicate check
    # ------------------------------------------------------------------
    try:
        is_duplicate = _check_duplicate(validated.username, validated.email)
    except Exception as exc:
        log.error("Duplicate check failed", step="duplicate_check", error=str(exc))
        return ServiceResponse(
            status=Status.ERROR,
            message="Unable to process your request at this time. Please try again later.",
        )

    if is_duplicate:
        return ServiceResponse(
            status=Status.ERROR,
            message="username or email already taken.",   # intentionally vague — anti-enumeration
        )

    # ------------------------------------------------------------------
    # STEP 3 — Hash password
    # ------------------------------------------------------------------
    log.info("Hashing password", step="hash_password")
    try:
        hashed_pw = _hash_password(validated.password)
    except Exception as exc:
        log.error("Password hashing failed", step="hash_password", error=str(exc))
        return ServiceResponse(
            status=Status.ERROR,
            message="Unable to process your request at this time. Please try again later.",
        )
    log.info("Password hashed", step="hash_password", status="ok")

    # --------------------------------------------------------------------------------------------------
    # STEP 4 — Build DB payload (user_id will be automatically generated on the DB side upon insertion)
    # --------------------------------------------------------------------------------------------------

    db_payload = {
        "username":  validated.username,
        "email":     validated.email,
        "password":  hashed_pw,
        "full_name": validated.full_name,
    }
    log.info("DB payload prepared", step="build_payload")

    # ------------------------------------------------------------------
    # STEP 5 — Insert into Supabase
    # ------------------------------------------------------------------
    try:
        created_row = _insert_user(db_payload)
    except Exception as exc:
        log.error("DB insert failed", step="db_insert", error=str(exc))
        return ServiceResponse(
            status=Status.ERROR,
            message="Unable to create your account at this time. Please try again later.",
        )

    # ------------------------------------------------------------------
    # STEP 6 — Return success (never expose hashed password in response)
    # ------------------------------------------------------------------
    log.info(
        "Account created successfully",
        step="complete",
        status="ok"
    )
    return ServiceResponse(
        status=Status.SUCCESS,
        message="Account created successfully! Welcome aboard.",
        data={
            "username": created_row["username"],
            "email":    created_row["email"],
        },
    )


# ---------------------------------------------------------------------------
# Minimal manual smoke-test  (comment out before deploying)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import json

    tests = [
        (
            "✅ Valid new user",
            {
                "username": "john_doe",
                "password": "Secure@123",
                "email":    "john.doe@gmail.com",
                "full_name": "John Doe",
            },
        ),
        (
            "❌ Multiple validation errors",
            {
                "username": "jd",           # too short
                "password": "weakpass",     # no special char
                "email":    "bad@yahoo.com",
            },
        ),
    ]

    for label, payload in tests:
        print(f"\n{'='*60}\nTest: {label}")
        result = create_account(payload)
        print(json.dumps(result.to_dict(), indent=2))