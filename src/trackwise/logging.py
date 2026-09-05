import structlog

def configure_logging(log_level: str) -> None:
    
    structlog.configure(
        processors=[
            # Filter by severity levels
            structlog.stdlib.filter_by_level,
            # Add TimeStamp to each entry in ISO 8601 format
            structlog.processors.TimeStamper(fmt="iso"),
            # Add Log Level to each entry
            structlog.stdlib.add_log_level,
            # Format Exceptions if present
            structlog.processors.format_exc_info,
            # Take final dictionary as string
            structlog.processors.JSONRenderer()
        ]
    )