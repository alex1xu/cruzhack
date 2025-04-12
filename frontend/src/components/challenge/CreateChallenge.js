import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { challengeService } from '../../services/api';

const CreateChallenge = () => {
    const [photo, setPhoto] = useState(null);
    const [preview, setPreview] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const { user } = useAuth();
    const navigate = useNavigate();

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
            await challengeService.createChallenge(user.user_id, photo);
            navigate('/');
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to create challenge');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="row justify-content-center">
            <div className="col-md-8">
                <div className="card">
                    <div className="card-body">
                        <h2 className="text-center mb-4">Create Challenge</h2>
                        {error && <div className="alert alert-danger">{error}</div>}
                        <form onSubmit={handleSubmit}>
                            <div className="mb-3">
                                <label htmlFor="photo" className="form-label">
                                    Challenge Photo
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
                                className="btn btn-primary w-100"
                                disabled={loading}
                            >
                                {loading ? 'Creating Challenge...' : 'Create Challenge'}
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CreateChallenge; 