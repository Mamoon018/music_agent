
from src.models.users import UserCredentialsModel
from src.utils import logger


# ---------------------------------------------------------------------------
# users.py  --  Quick self-test 
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


