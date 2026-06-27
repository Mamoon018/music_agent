

import structlog
import uuid
from typing import Any

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

# ---------------------------------------------------------------------------
# Identity constants  (replace with real auth/session source in production)
# ---------------------------------------------------------------------------
REQUEST_ID: str = f"112-{uuid.uuid4()}"   # 112 prefix + UUID4 → unique per request


# Bind shared context once — session_id flow into every log line
# automatically without being mentioned again.
# NOTE: We keep the variable name `logger` (not `log`) because structlog's
#       BoundLogger exposes a method called `.log()`, so naming the variable
#       `log` would shadow that method and cause AttributeError at call sites.

# When we will receive the HTTP request that will trigger the logger, we will fetch its
# service name and plug in its value here. OR we have to manually add service field into logs at every point.


logger = structlog.get_logger().bind(
    request_id=REQUEST_ID, service = Any | None
)