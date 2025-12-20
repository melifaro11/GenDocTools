import logging
logger = logging.getLogger("GenFilesMCP")

def _get_bearer_token(ctx):
    """Safely retrieve the Authorization header from the request context.

    Returns the header value as a string, or None if not present.
    """
    try:
        request_context = getattr(ctx, "request_context", None)
        request = getattr(request_context, "request", None)
        headers = getattr(request, "headers", None)
        if headers and hasattr(headers, "get"):
            return headers.get("authorization")
    except Exception:
        # Log unexpected errors with stack trace for debugging.
        logger.exception("Unexpected error retrieving authorization header")

    return None