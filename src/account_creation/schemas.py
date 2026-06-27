

from enum import Enum
from dataclasses import dataclass


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