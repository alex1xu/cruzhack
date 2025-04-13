import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Link } from 'react-router-dom';
import { challengeService } from '../../services/api';
import 'leaflet/dist/leaflet.css';
import "leaflet-draw/dist/leaflet.draw-src.css";
import 'leaflet-draw';
import L from 'leaflet';

// Fix for default marker icons in Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const ChallengeMap = () => {
    const [challenges, setChallenges] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchChallenges = async () => {
            try {
                const data = await challengeService.getChallenges();
                setChallenges(data);
            } catch (err) {
                setError('Failed to load challenges');
            } finally {
                setLoading(false);
            }
        };

        fetchChallenges();
    }, []);

    if (loading) {
        return <div className="text-center">Loading challenges...</div>;
    }

    if (error) {
        return <div className="alert alert-danger">{error}</div>;
    }

    return (
        <div className="challenge-map">
            <h2 className="mb-4">Available Challenges</h2>
            <div className="row">
                <div className="col-md-8">
                    <div style={{ height: '500px', width: '100%' }}>
                        <MapContainer center={[0, 0]} zoom={2} style={{ height: '100%', width: '100%' }}>
                            <TileLayer
                                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                            />
                            {challenges.map((challenge) => {
                                let markerPosition = [0, 0];
                                if (challenge.boundary) {
                                    // Ensure the boundary is an object:
                                    let boundary = challenge.boundary;
                                    if (typeof boundary === 'string') {
                                        try {
                                            boundary = JSON.parse(boundary);
                                        } catch (e) {
                                            console.error("Failed to parse boundary", e);
                                        }
                                    }
                                    // Wrap the geometry in a Feature for proper handling
                                    const geojsonFeature = {
                                        type: "Feature",
                                        geometry: boundary,
                                    };
                                    const bounds = L.geoJSON(geojsonFeature).getBounds();
                                    markerPosition = bounds.getCenter();
                                }
                                return (
                                    <Marker key={challenge.id} position={markerPosition}>
                                        <Popup>
                                            <div>
                                                <h5>{challenge.title}</h5>
                                                <p>{challenge.description}</p>
                                                <Link
                                                    to={`/challenge/${challenge.id}`}
                                                    className="btn btn-primary btn-sm"
                                                >
                                                    Play Challenge
                                                </Link>
                                            </div>
                                        </Popup>
                                    </Marker>
                                );
                            })}
                        </MapContainer>
                    </div>
                </div>
                <div className="col-md-4">
                    <div className="list-group">
                        {challenges.map((challenge) => (
                            <div key={challenge.id} className="list-group-item">
                                <h5 className="mb-1">{challenge.title}</h5>
                                <p className="mb-1">{challenge.description}</p>
                                <Link
                                    to={`/challenge/${challenge.id}`}
                                    className="btn btn-primary btn-sm"
                                >
                                    Play Challenge
                                </Link>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ChallengeMap;
