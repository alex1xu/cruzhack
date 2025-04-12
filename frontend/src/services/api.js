import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const authService = {
    register: async (username, password) => {
        const response = await api.post('/auth/register', {
            username,
            password,
        });
        return response.data;
    },

    login: async (username, password) => {
        const response = await api.post('/auth/login', {
            username,
            password,
        });
        return response.data;
    },
};

export const challengeService = {
    createChallenge: async (formData) => {
        const response = await api.post('/challenges', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    getChallenges: async () => {
        const response = await api.get('/challenges');
        return response.data;
    },

    getChallenge: async (id) => {
        const response = await api.get(`/challenges/${id}`);
        return response.data;
    },

    submitGuess: async (challengeId, userId, photo, guessCount) => {
        const formData = new FormData();
        formData.append('user_id', userId);
        formData.append('photo', photo);
        formData.append('guess_count', guessCount);

        const response = await api.post(`/challenges/${challengeId}/guess`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    getLeaderboard: async (challengeId) => {
        const response = await api.get(`/challenges/${challengeId}/leaderboard`);
        return response.data;
    },
}; 