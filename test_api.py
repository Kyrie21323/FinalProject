import requests

# Define the base URL of your FastAPI API
BASE_URL = "http://localhost:8000" # when we use uvicorn to run the API on our local machine it will generate a URL like this then we can use that to make requests to the API

# we can also implement the same in javascript using the fetch API for our frontend
# Function to get all influencers
def get_influencers():
    response = requests.get(f"{BASE_URL}/influencers")
    
    if response.status_code == 200:
        influencers = response.json()
        print("Influencers:")
        for influencer in influencers:
            print(influencer)
    else:
        print(f"Failed to fetch influencers. Status code: {response.status_code}")

# Function to get all content
def get_content():
    response = requests.get(f"{BASE_URL}/content")
    
    if response.status_code == 200:
        content = response.json()
        print("Content:")
        for item in content:
            print(item)
    else:
        print(f"Failed to fetch content. Status code: {response.status_code}")


# Function to update a vote (PUT request)
BASE_URL = "http://127.0.0.1:8000"

def update_vote(influencer_id, content_id, is_thumb_up):
    """
    Function to update a vote for a given influencer and content.
    
    Parameters:
    - influencer_id (int): The ID of the influencer.
    - content_id (int): The ID of the content.
    - is_thumb_up (bool): True if it's a thumbs up, False if it's a thumbs down.
    
    Returns:
    - None: Prints success or failure message based on the response.
    """
    
    # Step 1: Fetch current vote data from backend
    try:
        fetch_response = requests.get(f"{BASE_URL}/votes/{influencer_id}/{content_id}")
        print(fetch_response)
        if fetch_response.status_code == 404:
            print("Vote not found.")
            return
        elif fetch_response.status_code != 200:
            print(f"Failed to fetch current vote data. Status code: {fetch_response.status_code}")
            return
        
        current_vote = fetch_response.json()
        
        # Step 2: Update vote based on whether it's a thumbs up or thumbs down
        updated_vote = {
            "influencer_id": influencer_id,
            "content_id": content_id,
            "good_vote": current_vote['good_vote'] + 1 if is_thumb_up else current_vote['good_vote'],
            "bad_vote": current_vote['bad_vote'] + 1 if not is_thumb_up else current_vote['bad_vote']
        }

        # Step 3: Send PUT request to update vote in backend
        update_response = requests.put(f"{BASE_URL}/votes", json=updated_vote)
        
        if update_response.status_code == 200:
            print("Vote updated successfully:", update_response.json())
        else:
            print(f"Failed to update vote. Status code: {update_response.status_code}, Error: {update_response.text}")
    
    except requests.ConnectionError as e:
        print("Failed to connect:", e)

# Update a vote for influencer 18 and content 13 with a thumbs up


# Main function to run the app
if __name__ == "__main__":
    # Fetch all influencers
    get_influencers()

    # Fetch all content
    get_content()

    # Update an existing vote (replace with actual influencer_id and content_id)
    update_vote(18, 13, True)
    update_vote(18, 13, False)

    update_vote(19, 14, True)
    update_vote(19, 14, False)