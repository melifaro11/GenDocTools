from requests import post, get
from json import dumps
from io import BytesIO
import logging
logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger("GenFilesMCP")
from collections import defaultdict

def transform_list_of_knowledge_to_dict(knowledge_list: list) -> dict:
    """
    Transform a list of knowledge items into a nested dictionary structure.
    Args:
        knowledge_list (list): A list of knowledge items, each represented as a dictionary.
    Returns:
        dict: A nested dictionary where the first key is user_id, the second key is knowledge_name,
              and the value is a dictionary with knowledge_id and files_ids.
    """
    # Initialize the new dictionary
    knowledge_new_dict = defaultdict(defaultdict)

    # Iterate through each knowledge item in the list
    for element in knowledge_list:
        user_id = element['user_id']
        knowledge_id = element['id']
        knowledge_name = element['name']
        files_ids = element.get('data', []).get('file_ids',[])
        
        # Main key is user_id, secondary key is knowledge_name
        knowledge_new_dict[user_id][knowledge_name] = {
            'knowledge_id': knowledge_id,
            'files_ids': files_ids
        }
        
    return knowledge_new_dict

def check_knowledge_exists(url: str, token: str) -> dict:
    """
    Check if knowledge items exist at the specified URL with the provided token.
    
    Args:
        url (str): The base URL to check for knowledge items.
        token (str): The authorization token for the request.
    Returns:
        dict: A dictionary mapping knowledge item names to their IDs.
    """

    # Ensure the URL ends with '/api/v1/knowledge/list'
    endpoint = f'{url}/api/v1/knowledge/list'

    # Prepare headers for the request
    headers = {
        'Authorization': token,
        'Accept': 'application/json'
    }

    # Make the GET request to fetch the knowledge list
    response = get(endpoint, headers=headers)
    
    if response.status_code != 200:
        logger.error(f"Error fetching knowledge list, status code =>  {response.status_code}")
        return dumps({"error":{"message": f'Error creating knowledge'}})
    elif response.status_code == 200:
        # Parse the JSON response to get the list of knowledge items
        knowledge_list = response.json()
        knowledge_dict = transform_list_of_knowledge_to_dict(knowledge_list)
        logger.info("Knowledge items fetched successfully")
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
        logger.info("File added to knowledge base successfully.")
        return True
    else:
        logger.error(f"Error adding file to knowledge base, status code => {response.status_code}")
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
    # Check if the knowledge item already exists
    knowledge_dicts = check_knowledge_exists(url, token)
    
    if not isinstance(knowledge_dicts, dict):
        logger.error("Failed to check knowledge exists")
        return False

    # If it exists, do nothing; otherwise, create it.
    # knowledge_dicts is expected to be: {user_id: {knowledge_name: {'knowledge_id': ..., 'files_ids': [...]}}}
    if knowledge_dicts.get(user_id, {}).get(knowledge_name):

        # check if the file is already present
        current_files = knowledge_dicts[user_id][knowledge_name].get('files_ids', [])

        if file_id in current_files:
            logger.info(f"File {file_id} already exists in knowledge base. No action taken.")
            return True
        else:
            logger.info(f"File {file_id} not found in knowledge base {knowledge_name}. Proceeding to add the file.")

            # Add the uploaded file to the knowledge base
            add_file_state = add_file_to_knowledge(
                url=url,
                token=token,
                knowledge_id=knowledge_dicts[user_id][knowledge_name]['knowledge_id'],
                file_id=file_id
            )
        logger.info("Knowledge base already exists. Added file to existing knowledge base of user.")

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
            logger.info("Knowledge base created successfully.")

            # Get the new knowledge id
            knowledge_data = response.json()
            knowledge_id = knowledge_data.get('id')
            if not knowledge_id:
                logger.error("No id in response after creating knowledge")
                return False

            # Add the uploaded file to the knowledge base
            add_file_state = add_file_to_knowledge(
                url=original_url, 
                token=token, 
                knowledge_id=knowledge_id, 
                file_id=file_id
            )

            if add_file_state:
                logger.info("File added to knowledge base successfully.")
            else:
                logger.error(f"Error adding file to knowledge base")

            return True
        else:
            logger.error(f"Error creating knowledge base")
            return False 
