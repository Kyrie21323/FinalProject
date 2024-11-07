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
def update_vote(influencer_id, content_id, new_vote):
    params = {
        "influencer_id": influencer_id,
        "content_id": content_id,
        "new_vote": new_vote
    }
    response = requests.put(f"{BASE_URL}/votes/update", params=params)
    
    if response.status_code == 200:
        print("Vote updated successfully.")
    else:
        print(f"Failed to update vote. Status code: {response.status_code}, Error: {response.text}")

# Main function to run the app
if __name__ == "__main__":
    # Fetch all influencers
    get_influencers()

    # Fetch all content
    get_content()

    # Add a new vote (replace with actual influencer_id and content_id)
    add_vote(influencer_id=1, content_id=2, vote="upvote")

    # Update an existing vote (replace with actual influencer_id and content_id)
    update_vote(influencer_id=1, content_id=2, new_vote="downvote")