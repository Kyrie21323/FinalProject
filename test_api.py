import requests

# Define the base URL of your FastAPI API
BASE_URL = "http://127.0.0.1:8000"
 # when we use uvicorn to run the API on our local machine it will generate a URL like this then we can use that to make requests to the API

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
import requests

def update_vote(influencer_id, is_good_vote):
    """
    Update the vote for a given influencer by incrementing either good_vote or bad_vote by 1.

    Parameters:
    influencer_id (int): The ID of the influencer.
    is_good_vote (bool): If True, increment good votes. If False, increment bad votes.
    """
    
    # Prepare the data for updating the vote
    if is_good_vote:
        vote_update_data = {
            'good_vote': 1,  # Increment good vote by 1
            'bad_vote': 0    # No change to bad votes
        }
    else:
        vote_update_data = {
            'good_vote': 0,  # No change to good votes
            'bad_vote': 1    # Increment bad vote by 1
        }

    # URL pointing to the locally running FastAPI application
    url = f'http://127.0.0.1:8000/Votes/{influencer_id}'

    # Making a PUT request to update the vote
    try:
        response = requests.put(url, json=vote_update_data)
        if response.status_code == 200:
            print('Vote updated successfully:', response.json())
        elif response.status_code == 404:
            print('Vote not found:', response.text)
        else:
            print('Failed to update vote:', response.status_code, response.text)
    except requests.ConnectionError as e:
        print('Failed to connect:', e)



# Update a vote for influencer 18 and content 13 with a thumbs up


# Main function to run the app
if __name__ == "__main__":
    # Fetch all influencers
    get_influencers()
    # Fetch all content
    get_content()
    
    # Example usage:
    # To increment good vote (thumbs up) for influencer with ID 19
    update_vote(19, True)

    # To increment bad vote (thumbs down) for influencer with ID 1
    update_vote(5, False)

   