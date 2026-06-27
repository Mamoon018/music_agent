
from src.account_creation.service import create_account
import json


# ---------------------------------------------------------------------------
# Minimal manual smoke-test 
# ---------------------------------------------------------------------------
if __name__ == "__main__":

    tests = [
        (
            "✅ Valid new user",
            {
                "username": "john_cena",
                "password": "bestllname@123",
                "email":    "cena.joe@gmail.com",
                "full_name": "Johnie cene",
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

    counter = 0
    for label, payload in tests:
        tests_len = len(tests)
        counter += 1
        print(f"\n{'='*60}\nTest: {label}")
        result = create_account(payload)
        print(json.dumps(result.to_dict(), indent=2))

        if counter == tests_len:
            with open("src/account_creation/sample_output.json", "w") as file:
                json.dump(result.to_dict(), file, indent=4)

        


