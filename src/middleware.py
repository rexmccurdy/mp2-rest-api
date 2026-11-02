import logging
import time
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def log_requests(request: Request, call_next):
    """Log one request and attach its request ID to the response."""
    request_id = uuid.uuid4().hex[:8]
    request.state.request_id = request_id
    started = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        logger.error(f"Request ID {request_id} unexpectedly failed", exc_info=True)

        response = JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

    duration_ms = (time.perf_counter() - started) * 1000

    message = (
        f"Request ID: {request_id}, Method: {request.method}, URL: {request.url.path}, "
        f"Response: {response.status_code}, Duration: {duration_ms:.2f} ms"
    )
    if 500 <= response.status_code < 600:
        logger.error(message)
    elif 400 <= response.status_code < 500:
        logger.warning(message)
    else:
        logger.info(message)
    # TODO 2: Build a message containing request_id, request.method,
    # request.url.path, response.status_code, and duration_ms.
    # TODO 3: Log that message at ERROR for 5xx, WARNING for 4xx,
    # and INFO for other responses.

    response.headers["X-Request-ID"] = request_id
    return response
