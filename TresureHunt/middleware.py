from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from config import settings

limiter = Limiter(key_func=get_remote_address)

security_middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_methods=["POST", "GET"],
        allow_headers=["Content-Type"],
        max_age=3600
    )
]

def get_rate_limiter():
    return limiter