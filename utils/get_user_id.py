"""
Utility functions for retrieving user information from the server.
"""

from requests import get
from utils.logger import get_logger

logger = get_logger(__name__)


def get_user_id(url: str, token: str) -> str | None:
    """
    Retrieve only the current session `user_id`.

    Args:
        url (str): Base URL of the API (e.g. http://host:port)
        token (str): Bearer token string to use in the Authorization header

    Returns:
        str | None: The `user_id` string on success, or `None` on any error.

    Behavior:
        - Tries a GET to `{url}/api/v1/auths/` and parses the JSON response.
        - Attempts to extract `id` from common locations in the response
          (top-level `id`, `user.id`, or `data.id`). If not found returns None.

    Note: This function intentionally returns only the id (or None) as requested.
    """

    endpoint = f"{url.rstrip('/')}/api/v1/auths/"
    headers = {
        'Authorization': token,
        'Accept': 'application/json'
    }

    try:
        resp = get(endpoint, headers=headers, timeout=10)
    except Exception:
        logger.error("=> Error retrieving user id.")
        return None

    if resp.status_code != 200:
        logger.error(f"=> Error retrieving user id. Status code: {resp.status_code}")
        return None

    try:
        data = resp.json()
    except Exception:
        logger.error("=> Error retrieving user id json decoding.")
        return None

    # Return the top-level 'id' if present, else None
    return data.get('id') if isinstance(data, dict) else None
