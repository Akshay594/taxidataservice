# src/utils/logging.py

import logging
import json
from datetime import datetime
from typing import Dict, Any
import structlog
from pythonjsonlogger import jsonlogger

def setup_logging(service_name: str = "taxi-trip-service"):
    """
    Configure structured logging for the application.
    """
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Create custom JSON formatter
    class CustomJsonFormatter(jsonlogger.JsonFormatter):
        def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
            super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
            log_record['service'] = service_name
            log_record['timestamp'] = datetime.utcnow().isoformat()
            log_record['level'] = record.levelname
            log_record['correlation_id'] = getattr(record, 'correlation_id', None)

    # Configure root logger
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return structlog.get_logger()

class LoggerMiddleware:
    """
    Middleware to add request logging.
    """
    
    def __init__(self, app):
        self.app = app
        self.logger = setup_logging()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        start_time = datetime.utcnow()
        
        # Log request
        self.logger.info(
            "request_started",
            path=scope["path"],
            method=scope["method"]
        )

        try:
            response = await self.app(scope, receive, send)
            
            # Log response
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.info(
                "request_completed",
                path=scope["path"],
                method=scope["method"],
                duration=duration,
                status_code=response.status_code
            )
            
            return response
            
        except Exception as e:
            self.logger.error(
                "request_failed",
                path=scope["path"],
                method=scope["method"],
                error=str(e)
            )
            raise

# Example usage in main.py:
"""
from src.utils.logging import setup_logging, LoggerMiddleware

logger = setup_logging()
app.add_middleware(LoggerMiddleware)

# Then use logger in your code:
logger.info("Processing trip data", trip_id=123, duration=45)
"""