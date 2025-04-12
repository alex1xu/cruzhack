import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { useAuth } from './contexts/AuthContext';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import ChallengeMap from './components/challenge/ChallengeMap';
import CreateChallenge from './components/challenge/CreateChallenge';
import PlayChallenge from './components/challenge/PlayChallenge';
import Navbar from './components/common/Navbar';

const PrivateRoute = ({ children }) => {
    const { user, loading } = useAuth();

    if (loading) {
        return <div>Loading...</div>;
    }

    return user ? children : <Navigate to="/login" />;
};

function App() {
    return (
        <AuthProvider>
            <Router>
                <div className="App">
                    <Navbar />
                    <div className="container mt-4">
                        <Routes>
                            <Route path="/login" element={<Login />} />
                            <Route path="/register" element={<Register />} />
                            <Route
                                path="/"
                                element={
                                    <PrivateRoute>
                                        <ChallengeMap />
                                    </PrivateRoute>
                                }
                            />
                            <Route
                                path="/create-challenge"
                                element={
                                    <PrivateRoute>
                                        <CreateChallenge />
                                    </PrivateRoute>
                                }
                            />
                            <Route
                                path="/challenge/:id"
                                element={
                                    <PrivateRoute>
                                        <PlayChallenge />
                                    </PrivateRoute>
                                }
                            />
                        </Routes>
                    </div>
                </div>
            </Router>
        </AuthProvider>
    );
}

export default App; 