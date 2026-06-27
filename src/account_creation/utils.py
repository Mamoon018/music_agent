

import bcrypt
import os
from supabase import create_client, Client
from dotenv import load_dotenv

from src.utils import logger

# ---------------------------------------------------------------------------
# Supabase client  (reads credentials from env — never hard-code secrets)
# ---------------------------------------------------------------------------

load_dotenv(".env.dev")                          # loads SUPABASE_URL and SUPABASE_KEY from .env
_SUPABASE_URL: str = os.environ["SUPABASE_URL"]
_SUPABASE_KEY: str = os.environ["SUPABASE_KEY"]

supabase: Client = create_client(_SUPABASE_URL, _SUPABASE_KEY)


# --------------------------
# Constant variables 
# --------------------------
USERS_TABLE = "users"


# --------------------------------------------------------------------
# Internal helpers
# --------------------------------------------------------------------

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
