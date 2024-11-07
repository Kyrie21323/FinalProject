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

// Function to add a vote (POST request)
async function addVote(influencerId, contentId, vote) {
    try {
        const response = await axios.post(`${BASE_URL}/votes`, {
            influencer_id: influencerId,
            content_id: contentId,
            vote: vote
        });
        
        console.log("Vote added successfully");
    } catch (error) {
        console.error("Error adding vote:", error.response ? error.response.status : error.message);
    }
}

// Function to update a vote (PUT request)
async function updateVote(influencerId, contentId, newVote) {
    try {
        const response = await axios.put(`${BASE_URL}/votes/update`, null, { 
            params: { 
                influencer_id: influencerId,
                content_id: contentId,
                new_vote: newVote 
            }
        });
        
        console.log("Vote updated successfully");
    } catch (error) {
        console.error("Error updating vote:", error.response ? error.response.status : error.message);
    }
}

// Example usage:
getInfluencers(); // Fetch all influencers
getContent(); // Fetch all content
addVote(1, 2, "upvote"); // Add a new vote
updateVote(1, 2, "downvote"); // Update an existing vote