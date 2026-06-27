"""
user_validation_model.py
------------------------
Pydantic model for validating incoming user credentials from the API
before persisting them to the database.
"""
"""
Pydantic model for validating incoming user credentials from the API
before persisting them to the database.
 
Logging: structlog with JSONRenderer so every log line is a valid JSON
object ready for ingestion into a central log platform.
"""
 
import re
from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from src.utils import logger


# ---------------------------------------------------------------------------
# Constants (single source of truth for all rules)
# ---------------------------------------------------------------------------
USERNAME_MAX_LENGTH: int = 20
USERNAME_MIN_LENGTH: int = 3
PASSWORD_MIN_LENGTH: int = 8
PASSWORD_MAX_LENGTH: int = 128
ALLOWED_EMAIL_DOMAIN: str = "@gmail.com"

# At least one letter, one digit, one special character
_SPECIAL_CHARS = r"!@#$%^&*()_\-+=\[\]{};':\"\\|,.<>/?`~"
_PASSWORD_PATTERN = re.compile(
    rf"^(?=.*[A-Za-z])(?=.*\d)(?=.*[{_SPECIAL_CHARS}])[A-Za-z\d{_SPECIAL_CHARS}]{{{PASSWORD_MIN_LENGTH},{PASSWORD_MAX_LENGTH}}}$"
)

# Only alphanumeric + underscores for username (common safe choice)
_USERNAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


# ---------------------------------------------------------------------------
# Pydantic model
# ---------------------------------------------------------------------------
class UserCredentialsModel(BaseModel):
    """
    Validates user credentials received from the API before
    they are written to the database.

    Fields
    ------
    username : str
        Required. 3–20 characters, starts with a letter,
        alphanumeric + underscores only.
    password : str
        Required. 8–128 characters, alphanumeric + at least
        one special character.
    email : str
        Required. Must end with '@gmail.com'.
    full_name : str | None
        Optional display name (≤ 100 characters).
    """

    username: str
    password: str
    email: str
    full_name: Optional[str] = None

    # ------------------------------------------------------------------
    # Field-level validators
    # ------------------------------------------------------------------

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.strip()
        logger.info("Validating username …", field="username")

        if not value:
            raise ValueError("Username must not be empty.")

        if not (USERNAME_MIN_LENGTH <= len(value) <= USERNAME_MAX_LENGTH):
            raise ValueError(
                f"Username must be between {USERNAME_MIN_LENGTH} and "
                f"{USERNAME_MAX_LENGTH} characters (got {len(value)})."
            )

        if not _USERNAME_PATTERN.match(value):
            raise ValueError(
                "Username must start with a letter and contain only "
                "letters, digits, or underscores."
            )

        logger.info("Username validation passed", field="username", status="ok")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        logger.info("Validating password …", field="password")

        if not value:
            raise ValueError("Password must not be empty.")

        if not _PASSWORD_PATTERN.match(value):
            raise ValueError(
                f"Password must be {PASSWORD_MIN_LENGTH}–{PASSWORD_MAX_LENGTH} characters long, "
                "contain at least one letter, one digit, and one special character "
                f"(e.g. {_SPECIAL_CHARS[:8]} …)."
            )

        logger.info("Password validation passed", field="password", status="ok")
        return value  # store as-is; hash it in the service layer before DB insert

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        logger.info("Validating email …", field="email")

        if not value:
            raise ValueError("Email must not be empty.")

        if not value.endswith(ALLOWED_EMAIL_DOMAIN):
            raise ValueError(
                f"Email must be a Gmail address ending with '{ALLOWED_EMAIL_DOMAIN}'."
            )

        # Basic structural check: something before @gmail.com
        local_part = value[: -len(ALLOWED_EMAIL_DOMAIN)]
        if not local_part or not re.match(r"^[A-Za-z0-9._%+\-]+$", local_part):
            raise ValueError(
                "Email local part (before @gmail.com) is invalid. "
                "Only letters, digits, dots, underscores, percent, plus, and hyphens are allowed."
            )

        logger.info("Email validation passed", field="email", status="ok")
        return value

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if len(value) > 100:
            raise ValueError("Full name must not exceed 100 characters.")
        logger.info("Full-name validation passed", field="full_name", status="ok")
        return value

    # ------------------------------------------------------------------
    # Cross-field / model-level validators
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def password_must_not_contain_username(self) -> "UserCredentialsModel":
        """Prevent trivially guessable passwords like 'john1234!'."""
        logger.info("Running cross-field check", check="password_not_contains_username")
        if self.username.lower() in self.password.lower():
            raise ValueError("Password must not contain the username.")
        logger.info("Cross-field validation passed", check="password_not_contains_username", status="ok")
        return self

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------

    def safe_dict(self) -> dict:
        """
        Return a dict safe to log/display — password is masked.
        Never log the raw password.
        """
        return {
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "password": "********",
        }


# ---------------------------------------------------------------------------
# Quick self-test (remove / comment out in production)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from pydantic import ValidationError

    test_cases = [
        # (label, payload)
        (
            "✅ Valid user",
            {
                "username": "john_doe",
                "password": "Secure@123",
                "email": "john.doe@gmail.com",
                "full_name": "John Doe",
            },
        ),
        (
            "❌ Username too short",
            {"username": "jd", "password": "Secure@123", "email": "jd@gmail.com"},
        ),
        (
            "❌ Password no special char",
            {
                "username": "alice99",
                "password": "AlicePass1",
                "email": "alice@gmail.com",
            },
        ),
        (
            "❌ Wrong email domain",
            {
                "username": "bob_smith",
                "password": "Bob@12345",
                "email": "bob@yahoo.com",
            },
        ),
        (
            "❌ Password contains username",
            {
                "username": "charlie",
                "password": "charlie@99X",
                "email": "charlie@gmail.com",
            },
        ),
    ]

    for label, payload in test_cases:
        print(f"\n{'='*60}")
        print(f"Test: {label}")
        try:
            user = UserCredentialsModel(**payload)
            logger.info(
                "Model instantiated successfully",
                result="success",
                safe_payload=user.safe_dict(),
            )
        except ValidationError as exc:
           logger.error(
                "Validation failed",
                result="failure",
                errors=exc.errors(),
            )


