"""
-----------------
Service layer for the "Create Account" endpoint.

Process flow:
    Request → Pydantic Validation → DB Duplicate Check → Hash Password → Store → Return Response

Dependencies:
    pip install pydantic bcrypt supabase structlog python-dotenv
"""

from typing import Any

from pydantic import ValidationError

# Import the Pydantic model from users.py (same package / directory)
from src.models.users import UserCredentialsModel
from src.account_creation.utils import _check_duplicate, _hash_password, _insert_user
from src.account_creation.schemas import Status, ServiceResponse
from src.utils import logger


# ---------------------------------------------------------------------------
# Public service function  (called by the FastAPI endpoint handler)
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

    logger.info("create_account request received", step="start")

    # ------------------------------------------------------------------
    # STEP 1 — Pydantic validation
    # ------------------------------------------------------------------
    logger.info("Running Pydantic validation", step="pydantic_validation")

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
        logger.warning(
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

    logger.info("Pydantic validation passed", step="pydantic_validation", status="ok")

    # ------------------------------------------------------------------
    # STEP 2 — Duplicate check
    # ------------------------------------------------------------------
    try:
        is_duplicate = _check_duplicate(validated.username, validated.email)
    except Exception as exc:
        logger.error("Duplicate check failed", step="duplicate_check", error=str(exc))
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
    logger.info("Hashing password", step="hash_password")
    try:
        hashed_pw = _hash_password(validated.password)
    except Exception as exc:
        logger.error("Password hashing failed", step="hash_password", error=str(exc))
        return ServiceResponse(
            status=Status.ERROR,
            message="Unable to process your request at this time. Please try again later.",
        )
    logger.info("Password hashed", step="hash_password", status="ok")

    # --------------------------------------------------------------------------------------------------
    # STEP 4 — Build DB payload (user_id will be automatically generated on the DB side upon insertion)
    # --------------------------------------------------------------------------------------------------

    db_payload = {
        "username":  validated.username,
        "email":     validated.email,
        "password":  hashed_pw,
        "full_name": validated.full_name,
    }
    logger.info("DB payload prepared", step="build_payload")

    # ------------------------------------------------------------------
    # STEP 5 — Insert into Supabase
    # ------------------------------------------------------------------
    try:
        created_row = _insert_user(db_payload)
    except Exception as exc:
        logger.error("DB insert failed", step="db_insert", error=str(exc))
        return ServiceResponse(
            status=Status.ERROR,
            message="Unable to create your account at this time. Please try again later.",
        )

    # ------------------------------------------------------------------
    # STEP 6 — Return success (never expose hashed password in response)
    # ------------------------------------------------------------------
    logger.info(
        "Account created successfully",
        step="complete",
        status="ok"
    )
    return ServiceResponse(
        status=Status.SUCCESS,
        message="Account created successfully! Welcome to Music-kie.",
        data={
            "username": created_row["username"],
            "email":    created_row["email"],
        },
    )

