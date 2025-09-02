from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class IPLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("ip_logger")

        # Create file handler for IP logging
        file_handler = logging.FileHandler("ip_requests.log")
        file_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Add handler to logger
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)

    async def dispatch(self, request: Request, call_next):
        # Get client IP address
        client_ip = request.client.host if request.client else "unknown"

        # Check for forwarded IP (if behind proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        # Get real IP if behind reverse proxy
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            client_ip = real_ip

        # Process request
        response = await call_next(request)

        # Log request details with IP
        log_message = (
            f"IP: {client_ip} | "
            f"Method: {request.method} | "
            f"URL: {request.url} | "
            f"User-Agent: {request.headers.get('user-agent', 'unknown')} | "
            f"Status: {response.status_code} | "
            f"Timestamp: {datetime.now().isoformat()}"
        )

        self.logger.info(log_message)

        # Add IP to response headers for debugging
        response.headers["X-Client-IP"] = client_ip

        return response
