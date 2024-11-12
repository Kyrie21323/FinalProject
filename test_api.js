// Import axios
import axios from 'axios';

// Base URL of your FastAPI backend
const BASE_URL = "http://localhost:8000";

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
async function updateVote(influencerId, contentId, isThumbUp) {
    try {
        // Step 1: Fetch the current vote data
        const fetchResponse = await axios.get(`${BASE_URL}/votes/${influencerId}/${contentId}`);
        const currentVote = fetchResponse.data;

        // Step 2: Update the vote values based on thumb up or thumb down
        const updatedVote = {
            influencer_id: influencerId,
            content_id: contentId,
            good_vote: isThumbUp ? currentVote.good_vote + 1 : currentVote.good_vote,
            bad_vote: isThumbUp ? currentVote.bad_vote : currentVote.bad_vote + 1
        };

        // Step 3: Send PUT request to update the vote in the backend
        const updateResponse = await axios.put(`${BASE_URL}/votes`, updatedVote);

        console.log("Vote updated successfully:", updateResponse.data);
    } catch (error) {
        console.error("Error updating vote:", error.response ? error.response.status : error.message);
    }
}

// Example usage:
getInfluencers(); // Fetch all influencers
getContent(); // Fetch all content

// Example usage when user clicks thumbs up
document.getElementById('thumb-up').addEventListener('click', () => {
    updateVote(2, 11, true);  // true means thumbs up (increment good vote)
});

// Example usage when user clicks thumbs down
document.getElementById('thumb-down').addEventListener('click', () => {
    updateVote(2, 11, false);  // false means thumbs down (increment bad vote)
});

