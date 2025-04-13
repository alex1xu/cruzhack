import axios from 'axios';

const api = axios.create({
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
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
        return eval(response.data);
    },

    getChallenge: async (id) => {
        const response = await api.get(`/challenges/${id}`);
        return response.data;
    },

    submitGuess: async (challengeId, formData) => {
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