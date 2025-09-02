from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)

        # Configure file handler
        self.file_handler = logging.FileHandler("logs/requests.log")
        self.file_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(formatter)

        # Create logger
        self.logger = logging.getLogger("request_logger")
        self.logger.addHandler(self.file_handler)
        self.logger.setLevel(logging.INFO)

    async def dispatch(self, request: Request, call_next):
        """Log request details and process time"""
        start_time = time.time()

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Process request
        response = await call_next(request)

        # Calculate process time
        process_time = time.time() - start_time

        # Log request details
        log_message = (
            f"Method: {request.method} | "
            f"URL: {request.url} | "
            f"IP: {client_ip} | "
            f"Status: {response.status_code} | "
            f"Process Time: {process_time:.4f}s"
        )

        self.logger.info(log_message)

        return response
