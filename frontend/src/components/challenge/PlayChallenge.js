import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, GeoJSON } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import "leaflet-draw/dist/leaflet.draw-src.css";
import 'leaflet-draw';
import { Form, Input, Button, Card, message, Typography, Upload } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { challengeService } from '../../services/api';
import { useParams } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const { Title, Text } = Typography;

const PlayChallenge = () => {
    const { id: challengeId } = useParams();
    const [challenge, setChallenge] = useState(null);
    const [guessCount, setGuessCount] = useState(0);
    const [feedback, setFeedback] = useState('');
    const [loading, setLoading] = useState(false);
    const [guessHistory, setGuessHistory] = useState([]);
    const [leaderboard, setLeaderboard] = useState([]);
    const [mapCenter, setMapCenter] = useState([0, 0]);

    const [form] = Form.useForm();
    const { user } = useAuth();

    // Load challenge data and leaderboard on component mount or when challengeId changes
    useEffect(() => {
        loadChallenge();
        loadLeaderboard();
    }, [challengeId]);

    const loadChallenge = async () => {
        try {
            const data = await challengeService.getChallenge(challengeId);
            setChallenge(data);
            // If boundary exists, try to set the map center to its first coordinate
            if (data.boundary) {
                // Parse the stored boundary (which is saved as a string)
                const boundaryGeo = JSON.parse(data.boundary[0]);
                // Wrap it as a GeoJSON Feature (if needed)
                const feature = {
                    type: "Feature",
                    properties: {},
                    geometry: boundaryGeo
                };
                // Create a Leaflet GeoJSON layer to calculate bounds
                const layer = L.geoJSON(feature);
                if (layer.getBounds()) {
                    const bounds = layer.getBounds();
                    setMapCenter(bounds.getCenter());
                    // Set a reasonable zoom level that shows the entire boundary
                    const map = document.querySelector('.leaflet-container');
                    if (map) {
                        const mapInstance = map._leaflet_map;
                        if (mapInstance) {
                            mapInstance.fitBounds(bounds, {
                                padding: [50, 50],
                                maxZoom: 15
                            });
                        }
                    }
                }
            }
        } catch (error) {
            message.error('Failed to load challenge');
        }
    };

    const loadLeaderboard = async () => {
        try {
            const data = await challengeService.getLeaderboard(challengeId);
            setLeaderboard(data);
        } catch (error) {
            message.error('Failed to load leaderboard');
        }
    };

    const handleSubmit = async (values) => {
        if (!values.photo) {
            message.error('Please upload a photo');
            return;
        }

        setLoading(true);
        try {
            const formData = new FormData();
            formData.append('user_id', user.user_id);
            formData.append('username', user.username);
            formData.append('photo', values.photo[0].originFileObj);
            formData.append('guess_count', guessCount + 1);

            const response = await challengeService.submitGuess(challengeId, formData);
            setFeedback(response.feedback);
            setGuessCount((prev) => prev + 1);

            // Append the current guess result to the local history
            setGuessHistory((prev) => [
                ...prev,
                { guess: guessCount + 1, feedback: response.feedback, correct: response.correct }
            ]);

            if (response.correct) {
                message.success('Congratulations! You found the correct location!');
                // Refresh leaderboard if the guess is correct
                loadLeaderboard();
            }
        } catch (error) {
            message.error('Failed to submit guess');
        } finally {
            setLoading(false);
            // Optionally, reset the form for the next guess
            form.resetFields();
        }
    };

    if (!challenge) {
        return <div>Loading...</div>;
    }

    // Prepare the GeoJSON data if a boundary exists
    let geoJsonData = null;
    if (challenge.boundary) {
        try {
            const boundaryGeo = challenge.boundary;
            geoJsonData = {
                type: "Feature",
                properties: {},
                geometry: boundaryGeo,
            };
        } catch (e) {
            console.error("Error parsing challenge boundary:", e);
        }
    }

    return (
        <div style={{ padding: '20px' }}>
            {/* Challenge title and description */}
            <Card>
                <Title level={2}>{challenge.title}</Title>
                <Text>{challenge.description}</Text>
            </Card>

            {/* Map displaying the challenge region */}
            {geoJsonData && (
                <Card style={{ marginTop: '20px' }}>
                    <Title level={3}>Challenge Region</Title>
                    <MapContainer
                        center={mapCenter}
                        zoom={12}
                        style={{ height: '400px', width: '100%' }}
                        whenCreated={(map) => {
                            // Fit the map view to the boundary's bounds
                            const layer = L.geoJSON(geoJsonData);
                            if (layer.getBounds().isValid()) {
                                map.fitBounds(layer.getBounds());
                            }
                        }}
                    >
                        <TileLayer
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        />
                        <GeoJSON data={geoJsonData} />
                    </MapContainer>
                </Card>
            )}

            {/* Guess submission and guess history */}
            <Card style={{ marginTop: '20px' }}>
                <Title level={3}>Submit Your Guess</Title>
                <Form form={form} onFinish={handleSubmit} layout="vertical">
                    <Form.Item
                        name="photo"
                        label="Upload your guess photo"
                        valuePropName="fileList"
                        getValueFromEvent={(e) => Array.isArray(e) ? e : (e && e.fileList)}
                    >
                        <Upload
                            beforeUpload={() => false}
                            maxCount={1}
                        >
                            <Button icon={<UploadOutlined />}>Upload Photo</Button>
                        </Upload>
                    </Form.Item>

                    <Form.Item>
                        <Button type="primary" htmlType="submit" loading={loading}>
                            Submit Guess
                        </Button>
                    </Form.Item>
                </Form>

                {/* Feedback display */}
                {feedback && (
                    <Card style={{ marginTop: '20px' }}>
                        <Title level={4}>Feedback</Title>
                        <Text>{feedback}</Text>
                    </Card>
                )}

                {/* Guess History */}
                <Card style={{ marginTop: '20px' }}>
                    <Title level={4}>Guess History</Title>
                    {guessHistory.length > 0 ? (
                        <ul>
                            {guessHistory.map((guess, index) => (
                                <li key={index}>
                                    <Text strong>Guess #{guess.guess}:</Text> {guess.feedback} {guess.correct ? "(Correct)" : ""}
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <Text>No guesses made yet.</Text>
                    )}
                </Card>
            </Card>

            {/* Leaderboard Display */}
            <Card style={{ marginTop: '20px' }}>
                <Title level={4}>Leaderboard</Title>
                {leaderboard && leaderboard.length > 0 ? (
                    <ol>
                        {leaderboard.map((entry, index) => (
                            <li key={index}>
                                <Text>{entry.username} - {entry.guess_count} guess{entry.guess_count > 1 ? "es" : ""}</Text>
                            </li>
                        ))}
                    </ol>
                ) : (
                    <Text>No leaderboard available yet.</Text>
                )}
            </Card>
        </div>
    );
};

export default PlayChallenge;
