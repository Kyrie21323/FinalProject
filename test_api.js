// Import axios
import axios from 'axios';
const BASE_URL = "http://localhost:8000"; // Base URL of your FastAPI backend

// Function to fetch all influencers
async function getInfluencers() {
    try {
        const response = await axios.get(`${BASE_URL}/influencers`);
        console.log("Influencers:", response.data);
    } catch (error) {
        console.error("Error fetching influencers:", error.response ? error.response.status : error.message);
    }
}
// Function to fetch all content
async function getContent() {
    try {
        const response = await axios.get(`${BASE_URL}/content`);
        console.log("Content:", response.data);
    } catch (error) {
        console.error("Error fetching content:", error.response ? error.response.status : error.message);
    }
}
// Function to update a vote (PUT request)
// Function to update vote for an influencer
function updateVote(influencerId, isGoodVote) {
    // Prepare the data for updating the vote
    const voteUpdateData = isGoodVote
        ? { good_vote: 1, bad_vote: 0 }  // Increment good_vote by 1, no change to bad_vote
        : { good_vote: 0, bad_vote: 1 }; // Increment bad_vote by 1, no change to good_vote

    // URL pointing to the FastAPI endpoint
    const url = `http://127.0.0.1:8000/Votes/${influencerId}`;

    // Make a PUT request using fetch API
    fetch(url, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(voteUpdateData),
    })
    .then(response => {
        if (response.ok) {
            return response.json(); // Parse JSON response
        } else if (response.status === 404) {
            throw new Error('Vote not found');
        } else {
            throw new Error('Failed to update vote');
        }
    })
    .then(data => {
        console.log('Vote updated successfully:', data);
        // Optionally, update the UI here based on the response
    })
    .catch(error => {
        console.error('Error:', error.message);
    });
}

// Example usage:
// To increment good vote (thumbs up) for influencer with ID 19
document.getElementById('thumbsUpButton').addEventListener('click', () => {
    updateVote(19, true);  // true indicates thumbs up (good vote)
});

// To increment bad vote (thumbs down) for influencer with ID 19
document.getElementById('thumbsDownButton').addEventListener('click', () => {
    updateVote(19, false);  // false indicates thumbs down (bad vote)
});
