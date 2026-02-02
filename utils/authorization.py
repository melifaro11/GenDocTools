import logging
logger = logging.getLogger("Gen Files OpenAPI Tool Server")

def _get_bearer_token(request):
    """Safely retrieve the Authorization header from the request.

    Returns the header value as a string, or None if not present.
    """
    try:
        return request.headers.get("authorization")
    except Exception:
        # Log unexpected errors with stack trace for debugging.
        logger.exception("=> Unexpected error retrieving authorization header")

    return None 