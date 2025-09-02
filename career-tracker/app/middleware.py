from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware


class UserAgentMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user_agent = request.headers.get("user-agent")

        if not user_agent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User-Agent header is required"
            )

        # Process request
        response = await call_next(request)
        return response
