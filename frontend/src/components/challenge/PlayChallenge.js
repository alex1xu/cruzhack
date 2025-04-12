import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { challengeService } from '../../services/api';

const PlayChallenge = () => {
    const { id } = useParams();
    const { user } = useAuth();
    const navigate = useNavigate();

    const [challenge, setChallenge] = useState(null);
    const [photo, setPhoto] = useState(null);
    const [preview, setPreview] = useState('');
    const [guessCount, setGuessCount] = useState(1);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [leaderboard, setLeaderboard] = useState([]);

    useEffect(() => {
        const fetchChallenge = async () => {
            try {
                const data = await challengeService.getChallenges();
                const challengeData = data.find(c => c._id === id);
                if (!challengeData) {
                    setError('Challenge not found');
                    return;
                }
                setChallenge(challengeData);

                // Fetch leaderboard
                const leaderboardData = await challengeService.getLeaderboard(id);
                setLeaderboard(leaderboardData);
            } catch (err) {
                setError('Failed to load challenge');
            }
        };

        fetchChallenge();
    }, [id]);

    const handlePhotoChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setPhoto(file);
            setPreview(URL.createObjectURL(file));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        if (!photo) {
            setError('Please select a photo');
            setLoading(false);
            return;
        }

        try {
            const response = await challengeService.submitGuess(
                id,
                user.user_id,
                photo,
                guessCount
            );

            setResult(response);

            if (response.is_correct) {
                // Refresh leaderboard
                const leaderboardData = await challengeService.getLeaderboard(id);
                setLeaderboard(leaderboardData);
            } else {
                setGuessCount(guessCount + 1);
            }
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to submit guess');
        } finally {
            setLoading(false);
        }
    };

    if (!challenge) {
        return <div className="text-center">Loading challenge...</div>;
    }

    return (
        <div className="row">
            <div className="col-md-8">
                <div className="card mb-4">
                    <div className="card-body">
                        <h2 className="mb-4">Challenge #{challenge._id}</h2>
                        <p className="lead">{challenge.caption}</p>

                        {error && <div className="alert alert-danger">{error}</div>}

                        {result && (
                            <div className={`alert ${result.is_correct ? 'alert-success' : 'alert-info'}`}>
                                <h4>{result.is_correct ? 'Correct!' : 'Try Again'}</h4>
                                <p>{result.hint}</p>
                                {result.is_correct && (
                                    <p>Similarity: {(result.similarity * 100).toFixed(2)}%</p>
                                )}
                            </div>
                        )}

                        {!result?.is_correct && (
                            <form onSubmit={handleSubmit}>
                                <div className="mb-3">
                                    <label htmlFor="photo" className="form-label">
                                        Your Guess
                                    </label>
                                    <input
                                        type="file"
                                        className="form-control"
                                        id="photo"
                                        accept="image/*"
                                        onChange={handlePhotoChange}
                                        required
                                    />
                                    <small className="text-muted">
                                        Supported formats: PNG, JPG, JPEG. Max size: 16MB
                                    </small>
                                </div>
                                {preview && (
                                    <div className="mb-3">
                                        <img
                                            src={preview}
                                            alt="Preview"
                                            className="img-fluid rounded"
                                            style={{ maxHeight: '300px' }}
                                        />
                                    </div>
                                )}
                                <button
                                    type="submit"
                                    className="btn btn-primary"
                                    disabled={loading}
                                >
                                    {loading ? 'Submitting...' : 'Submit Guess'}
                                </button>
                            </form>
                        )}
                    </div>
                </div>
            </div>

            <div className="col-md-4">
                <div className="card">
                    <div className="card-body">
                        <h3>Leaderboard</h3>
                        <div className="list-group">
                            {leaderboard.map((entry, index) => (
                                <div key={index} className="list-group-item">
                                    <div className="d-flex justify-content-between">
                                        <span>#{index + 1}</span>
                                        <span>{entry.guesses} guesses</span>
                                    </div>
                                </div>
                            ))}
                            {leaderboard.length === 0 && (
                                <div className="list-group-item">
                                    No one has solved this challenge yet!
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PlayChallenge; 