import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Form, Input, Button, Card, message, Typography } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { challengeService } from '../../services/api';
import { useParams } from 'react-router-dom';

const { Title, Text } = Typography;

const PlayChallenge = () => {
    const { challengeId } = useParams();
    const [challenge, setChallenge] = useState(null);
    const [guessCount, setGuessCount] = useState(0);
    const [feedback, setFeedback] = useState('');
    const [loading, setLoading] = useState(false);
    const [form] = Form.useForm();

    useEffect(() => {
        loadChallenge();
    }, [challengeId]);

    const loadChallenge = async () => {
        try {
            const data = await challengeService.getChallenge(challengeId);
            setChallenge(data);
        } catch (error) {
            message.error('Failed to load challenge');
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
            formData.append('photo', values.photo[0].originFileObj);
            formData.append('guess_count', guessCount + 1);

            const response = await challengeService.submitGuess(challengeId, formData);
            setFeedback(response.feedback);
            setGuessCount(guessCount + 1);

            if (response.correct) {
                message.success('Congratulations! You found the correct location!');
                // Update leaderboard
                loadChallenge();
            }
        } catch (error) {
            message.error('Failed to submit guess');
        } finally {
            setLoading(false);
        }
    };

    if (!challenge) {
        return <div>Loading...</div>;
    }

    return (
        <div style={{ padding: '20px' }}>
            <Card>
                <Title level={2}>{challenge.title}</Title>
                <Text>{challenge.description}</Text>
            </Card>

            <div style={{ marginTop: '20px' }}>
                <Form
                    form={form}
                    onFinish={handleSubmit}
                    layout="vertical"
                >
                    <Form.Item
                        name="photo"
                        label="Upload your guess photo"
                        valuePropName="fileList"
                        getValueFromEvent={(e) => {
                            if (Array.isArray(e)) {
                                return e;
                            }
                            return e?.fileList;
                        }}
                    >
                        <Upload
                            beforeUpload={() => false}
                            maxCount={1}
                        >
                            <Button icon={<UploadOutlined />}>Upload Photo</Button>
                        </Upload>
                    </Form.Item>

                    <Form.Item>
                        <Button
                            type="primary"
                            htmlType="submit"
                            loading={loading}
                        >
                            Submit Guess
                        </Button>
                    </Form.Item>
                </Form>

                {feedback && (
                    <Card style={{ marginTop: '20px' }}>
                        <Title level={4}>Feedback</Title>
                        <Text>{feedback}</Text>
                    </Card>
                )}

                <Card style={{ marginTop: '20px' }}>
                    <Title level={4}>Your Progress</Title>
                    <Text>Guesses: {guessCount}</Text>
                </Card>
            </div>
        </div>
    );
};

export default PlayChallenge; 