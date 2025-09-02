from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time


class ResponseTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate process time
        process_time = time.time() - start_time

        # Add response time to headers
        response.headers["X-Process-Time"] = str(process_time)

        return response
