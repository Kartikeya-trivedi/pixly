"""
Logging middleware for FastAPI.
Provides request/response logging and performance monitoring.
"""

from fastapi import Request, Response
import time
import logging
from typing import Callable
import json

logger = logging.getLogger(__name__)


async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware for logging HTTP requests and responses.
    
    Args:
        request: FastAPI request object
        call_next: Next middleware/handler in chain
    
    Returns:
        FastAPI response object
    """
    # Start timing
    start_time = time.time()
    
    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    # Process request
    try:
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {response.status_code} "
            f"in {process_time:.3f}s for {request.method} {request.url.path}"
        )
        
        # Add performance header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        # Log error
        process_time = time.time() - start_time
        logger.error(
            f"Error: {str(e)} in {process_time:.3f}s "
            f"for {request.method} {request.url.path}"
        )
        raise
