from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.logger import logger
import time

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        logger.info(f"Incoming request: {request.method} {request.url}")
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"Outgoing response: {response.status_code} in {process_time:.2f}ms"
        )
        return response
