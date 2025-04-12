import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { challengeService } from '../../services/api';
import { MapContainer, TileLayer, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';
import 'leaflet-draw';

const LocationSearch = ({ onLocationFound }) => {
    const map = useMap();
    const [searchQuery, setSearchQuery] = useState('');

    const handleSearch = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch(
                `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}`
            );
            const data = await response.json();
            if (data.length > 0) {
                const { lat, lon } = data[0];
                map.setView([lat, lon], 15);
                onLocationFound({ lat, lon });
            }
        } catch (error) {
            console.error('Error searching location:', error);
        }
    };

    return (
        <div className="search-container" style={{ position: 'absolute', top: '10px', left: '50px', zIndex: 1000 }}>
            <form onSubmit={handleSearch} className="d-flex">
                <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search location..."
                    className="form-control"
                    style={{ width: '300px' }}
                />
                <button type="submit" className="btn btn-primary ms-2">Search</button>
            </form>
        </div>
    );
};

const CreateChallenge = () => {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [photo, setPhoto] = useState(null);
    const [preview, setPreview] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [boundary, setBoundary] = useState(null);
    const mapRef = useRef(null);
    const drawControlRef = useRef(null);
    const { user } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        if (mapRef.current) {
            const map = mapRef.current;
            const drawnItems = new L.FeatureGroup();
            map.addLayer(drawnItems);

            drawControlRef.current = new L.Control.Draw({
                draw: {
                    polygon: {
                        shapeOptions: {
                            color: '#3388ff',
                            fillColor: '#3388ff',
                            fillOpacity: 0.2
                        }
                    },
                    polyline: false,
                    rectangle: false,
                    circle: false,
                    marker: false,
                    circlemarker: false
                },
                edit: {
                    featureGroup: drawnItems
                }
            });

            map.addControl(drawControlRef.current);

            map.on(L.Draw.Event.CREATED, (e) => {
                const layer = e.layer;
                drawnItems.addLayer(layer);
                setBoundary(layer.toGeoJSON());
            });

            map.on(L.Draw.Event.DELETED, () => {
                setBoundary(null);
            });

            return () => {
                map.removeControl(drawControlRef.current);
            };
        }
    }, []);

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

        if (!boundary) {
            setError('Please draw a boundary region');
            setLoading(false);
            return;
        }

        try {
            const formData = new FormData();
            formData.append('title', title);
            formData.append('description', description);
            formData.append('photo', photo);
            formData.append('boundary', JSON.stringify(boundary));
            formData.append('user_id', user.user_id);

            await challengeService.createChallenge(formData);
            navigate('/');
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to create challenge');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container mt-4">
            <div className="row">
                <div className="col-md-6">
                    <div className="card">
                        <div className="card-body">
                            <h2 className="text-center mb-4">Create Challenge</h2>
                            {error && <div className="alert alert-danger">{error}</div>}
                            <form onSubmit={handleSubmit}>
                                <div className="mb-3">
                                    <label htmlFor="title" className="form-label">Title</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        id="title"
                                        value={title}
                                        onChange={(e) => setTitle(e.target.value)}
                                        required
                                    />
                                </div>
                                <div className="mb-3">
                                    <label htmlFor="description" className="form-label">Description</label>
                                    <textarea
                                        className="form-control"
                                        id="description"
                                        value={description}
                                        onChange={(e) => setDescription(e.target.value)}
                                        rows="3"
                                        required
                                    />
                                </div>
                                <div className="mb-3">
                                    <label htmlFor="photo" className="form-label">Challenge Photo</label>
                                    <input
                                        type="file"
                                        className="form-control"
                                        id="photo"
                                        accept="image/*"
                                        onChange={handlePhotoChange}
                                        required
                                    />
                                </div>
                                {preview && (
                                    <div className="mb-3">
                                        <img
                                            src={preview}
                                            alt="Preview"
                                            className="img-fluid rounded"
                                            style={{ maxHeight: '200px' }}
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
                <div className="col-md-6">
                    <div className="card">
                        <div className="card-body">
                            <h3 className="mb-3">Select Challenge Boundary</h3>
                            <div style={{ height: '500px', width: '100%' }}>
                                <MapContainer
                                    center={[0, 0]}
                                    zoom={2}
                                    style={{ height: '100%', width: '100%' }}
                                    ref={mapRef}
                                >
                                    <TileLayer
                                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                                    />
                                    <LocationSearch onLocationFound={() => { }} />
                                </MapContainer>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CreateChallenge; 