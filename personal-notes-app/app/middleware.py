from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class RequestCounterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.request_count = 0
        self.logger = logging.getLogger("request_counter")

    async def dispatch(self, request: Request, call_next):
        self.request_count += 1

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Process request
        response = await call_next(request)

        # Log request details with count
        log_message = (
            f"Request #{self.request_count} | "
            f"Method: {request.method} | "
            f"URL: {request.url} | "
            f"IP: {client_ip} | "
            f"Status: {response.status_code} | "
            f"Timestamp: {datetime.now().isoformat()}"
        )

        self.logger.info(log_message)

        # Add request count to response headers
        response.headers["X-Request-Count"] = str(self.request_count)

        return response
