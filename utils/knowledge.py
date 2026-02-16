from requests import post, get
from json import dumps
from io import BytesIO
from collections import defaultdict
from utils.logger import get_logger

logger = get_logger(__name__)

def transform_list_of_knowledge_to_dict(knowledge_list) -> dict:
    """
    Transform a list or paginated response of knowledge items into a nested dictionary.
    Args:
        knowledge_list (list or dict): Either a list of knowledge items or a paginated response
            dict containing an "items" list.
    Returns:
        dict: A nested dictionary where the first key is user_id, the second key is knowledge_name,
              and the value is a dictionary with knowledge_id and files_ids.
    """
    # Normalize input to a list of items
    if isinstance(knowledge_list, dict) and 'items' in knowledge_list:
        items = knowledge_list.get('items', [])
    else:
        items = knowledge_list or []

    # Initialize the new dictionary
    knowledge_new_dict = defaultdict(defaultdict)

    # Iterate through each knowledge item in the list
    for element in items:
        user_id = element.get('user_id')
        knowledge_id = element.get('id')
        knowledge_name = element.get('name')
        files_ids = element.get('data', {}).get('file_ids', [])

        if user_id is None or knowledge_name is None or knowledge_id is None:
            # skip malformed entries
            continue

        # Main key is user_id, secondary key is knowledge_name
        knowledge_new_dict[user_id][knowledge_name] = {
            'knowledge_id': knowledge_id,
            'files_ids': files_ids
        }

    return knowledge_new_dict

def check_knowledge_exists(url: str, token: str, query: str = None) -> dict:
    """
    Check if knowledge items exist at the specified URL with the provided token.
    Uses the paginated search endpoint (`/api/v1/knowledge/search`) and supports an optional
    `query` parameter (e.g. a `knowledge_name`) to narrow results. It will paginate through
    results until all items are fetched or until no more pages are available.

    Args:
        url (str): The base URL to check for knowledge items.
        token (str): The authorization token for the request.
        query (str, optional): Search query to filter knowledge items (e.g. knowledge name).

    Returns:
        dict: A nested dictionary mapping user_id -> knowledge_name -> {knowledge_id, files_ids}.
    """

    endpoint = f'{url}/api/v1/knowledge/search'

    # Prepare headers for the request
    headers = {
        'Authorization': token,
        'Accept': 'application/json'
    }

    aggregated_items = []
    page = 1

    while True:
        params = {'page': page}
        if query:
            params['query'] = query

        response = get(endpoint, headers=headers, params=params)

        if response.status_code != 200:
            logger.error(f"=> Error fetching knowledge list (page {page}), status code => {response.status_code}")
            # Return None to indicate failure so callers can detect and handle it
            return None

        data = response.json()

        # Support multiple response shapes: paginated dict with 'items' or plain list
        if isinstance(data, dict) and 'items' in data:
            items = data.get('items', [])
            total = data.get('total')
        elif isinstance(data, list):
            items = data
            total = None
        else:
            items = []
            total = None

        aggregated_items.extend(items)

        # If total is provided, stop when we've collected them all
        if total is not None:
            if len(aggregated_items) >= total:
                break
            else:
                page += 1
                continue

        # Otherwise, rely on the page size heuristic: if a page returns fewer than 30 items,
        # it's likely the last page (the API max page size is 30)
        if not items or len(items) < 30:
            break

        page += 1

    knowledge_dict = transform_list_of_knowledge_to_dict(aggregated_items)
    logger.info("=> Knowledge items fetched successfully")
    return knowledge_dict
    
def add_file_to_knowledge(url: str, token: str, knowledge_id: str, file_id: str) -> bool:
    """
    Add a file to a specified knowledge item.
    Args:
        url (str): The base URL to add the file to the knowledge item.
        token (str): The authorization token for the request.
        knowledge_id (str): The ID of the knowledge item.
        file_id (str): The ID of the file to be added.
    Returns:
        bool: True if the file was added successfully, False otherwise.
    """

    # Add a file to a specified knowledge item.
    url = f'{url}/api/v1/knowledge/{knowledge_id}/file/add'

    # Prepare headers and data for the request
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    # Prepare payload for the request
    data = {'file_id': file_id}

    # Make the POST request to add the file to the knowledge item
    response = post(url, headers=headers, json=data)

    # Return True if the file was added successfully, else False
    if response.status_code == 200:
        logger.info("=> File added to knowledge base successfully.")
        return True
    else:
        logger.error(f"=> Error adding file to knowledge base, status code => {response.status_code}")
        return False
    
def create_knowledge(url: str, token: str, file_id: str, user_id: str, knowledge_name: str = 'My Generated Files') -> bool:
    """
    Create a new knowledge item if it does not already exist.

    Args:
        url (str): The base URL to create the knowledge item.
        token (str): The authorization token for the request.
        file_id (str): The ID of the file to be added to the knowledge item.
        user_id (str): The ID of the user creating the knowledge item.
        knowledge_name (str): The name of the knowledge item to be created.
    
    Returns:
        bool: True if the knowledge item was created, False otherwise.
    """
    # Check if the knowledge item already exists using the search query (knowledge name)
    knowledge_dicts = check_knowledge_exists(url, token, query=knowledge_name)
    
    if not isinstance(knowledge_dicts, dict):
        logger.error("=> Failed to check knowledge exists")
        return False

    # If it exists, do nothing; otherwise, create it.
    # knowledge_dicts is expected to be: {user_id: {knowledge_name: {'knowledge_id': ..., 'files_ids': [...]}}}
    if knowledge_dicts.get(user_id, {}).get(knowledge_name):

        # check if the file is already present
        current_files = knowledge_dicts[user_id][knowledge_name].get('files_ids', [])

        if file_id in current_files:
            logger.info(f"=> File {file_id} already exists in knowledge base. No action taken.")
            return True
        else:
            logger.info(f"=> File {file_id} not found in knowledge base {knowledge_name}. Proceeding to add the file.")

            # Add the uploaded file to the knowledge base
            add_file_state = add_file_to_knowledge(
                url=url,
                token=token,
                knowledge_id=knowledge_dicts[user_id][knowledge_name]['knowledge_id'],
                file_id=file_id
            )
        logger.info("=> Knowledge base already exists. Added file to existing knowledge base of user.")

        return add_file_state
    else:
        # Ensure the URL ends with '/api/v1/knowledge/create'
        original_url = url
        url = f'{url}/api/v1/knowledge/create'

        # Prepare payload and headers for the request
        payload = {
            "name": knowledge_name,
            "description": "Collection of files created using GenFilesMCP",
        }

        # Prepare headers for the request
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }

        # Make the POST request to create the knowledge item
        response = post(url, headers=headers, data=dumps(payload))

        # Return True if created successfully, else False
        if response.status_code == 200:
            logger.info("=> Knowledge base created successfully.")

            # Get the new knowledge id
            knowledge_data = response.json()
            knowledge_id = knowledge_data.get('id')
            if not knowledge_id:
                logger.error("=> No id in response after creating knowledge")
                return False

            # Add the uploaded file to the knowledge base
            add_file_state = add_file_to_knowledge(
                url=original_url, 
                token=token, 
                knowledge_id=knowledge_id, 
                file_id=file_id
            )

            if add_file_state:
                logger.info("=> File added to knowledge base successfully.")
            else:
                logger.error(f"=> Error adding file to knowledge base")

            return True
        else:
            logger.error(f"=> Error creating knowledge base")
            return False 
