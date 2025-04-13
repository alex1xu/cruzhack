import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, GeoJSON } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import "leaflet-draw/dist/leaflet.draw-src.css";
import 'leaflet-draw';
import { Button, Card, List, message } from 'antd';
import { PlayCircleOutlined } from '@ant-design/icons';
import { challengeService } from '../../services/api';
import LocationSearch from '../common/LocationSearch';

const ChallengeView = () => {
    const [challenges, setChallenges] = useState([]);
    const [selectedChallenge, setSelectedChallenge] = useState(null);
    const [map, setMap] = useState(null);

    useEffect(() => {
        loadChallenges();
    }, []);

    const loadChallenges = async () => {
        try {
            const data = await challengeService.getChallenges();
            // Make sure to only set challenges if data is an array.
            setChallenges(Array.isArray(data) ? data : []);
        } catch (error) {
            message.error('Failed to load challenges');
        }
    };

    const handleLocationFound = (coordinates) => {
        if (map) {
            map.setView(coordinates, 15);
        }
    };

    const handleChallengeClick = (challenge) => {
        setSelectedChallenge(challenge);
        if (challenge.boundary) {
            const bounds = L.geoJSON(challenge.boundary).getBounds();
            map.fitBounds(bounds);
        }
    };

    const handlePlayChallenge = (challengeId) => {
        window.location.href = `/play/${challengeId}`;
    };

    return (
        <div style={{ display: 'flex', height: 'calc(100vh - 64px)' }}>
            <div style={{ flex: 1, height: '100%', position: 'relative' }}>
                <div style={{ position: 'absolute', top: '10px', left: '10px', zIndex: 1000 }}>
                    <LocationSearch onLocationFound={handleLocationFound} />
                </div>
                <MapContainer
                    center={[0, 0]}
                    zoom={2}
                    style={{ height: '100%', width: '100%' }}
                    whenCreated={setMap}
                >
                    <TileLayer
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    />
                    {challenges.map((challenge) => {
                        let center;
                        if (challenge.boundary) {
                            const bounds = L.geoJSON(challenge.boundary).getBounds();
                            center = bounds.getCenter();
                        } else {
                            center = [0, 0]; // Default position if no boundary is available.
                        }
                        return (
                            <Marker
                                key={challenge.id}
                                position={center}
                                eventHandlers={{
                                    click: () => handleChallengeClick(challenge),
                                }}
                            >
                                <Popup>
                                    <div>
                                        <h3>{challenge.title}</h3>
                                        <Button
                                            type="primary"
                                            icon={<PlayCircleOutlined />}
                                            onClick={() => handlePlayChallenge(challenge.id)}
                                        >
                                            Play Challenge
                                        </Button>
                                    </div>
                                </Popup>
                            </Marker>
                        );
                    })}
                    {selectedChallenge?.boundary && (
                        <GeoJSON
                            data={selectedChallenge.boundary}
                            style={{
                                color: '#3388ff',
                                fillColor: '#3388ff',
                                fillOpacity: 0.2,
                            }}
                        />
                    )}
                </MapContainer>
            </div>
            <div style={{ width: 300, padding: '20px', overflowY: 'auto' }}>
                <Card title="Leaderboard" style={{ marginBottom: '20px' }}>
                    {selectedChallenge ? (
                        <List
                            dataSource={selectedChallenge.leaderboard}
                            renderItem={(item) => (
                                <List.Item>
                                    {item.username}: {item.guesses} guesses
                                </List.Item>
                            )}
                        />
                    ) : (
                        <p>Select a challenge to view leaderboard</p>
                    )}
                </Card>
            </div>
        </div>
    );
};

export default ChallengeView;
