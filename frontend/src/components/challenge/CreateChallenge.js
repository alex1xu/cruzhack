import React, { useState, useRef, useEffect, useCallback } from 'react';
import { MapContainer, TileLayer, useMap, FeatureGroup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import "leaflet-draw/dist/leaflet.draw-src.css";
import 'leaflet-draw';
import { Form, Input, Button, Upload, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { challengeService } from '../../services/api';
import LocationSearch from '../common/LocationSearch';
import { useAuth } from '../../contexts/AuthContext';

const LeafletDrawControl = ({ onCreated, onDeleted, drawnItemsRef }) => {
    const map = useMap();

    useEffect(() => {
        const drawControl = new L.Control.Draw({
            draw: {
                polygon: {
                    shapeOptions: {
                        color: '#3388ff',
                        fillColor: '#3388ff',
                        fillOpacity: 0.2
                    },
                    allowIntersection: false,
                    drawError: {
                        color: '#b00b00',
                        message: 'Polygon cannot intersect itself'
                    }
                },
                polyline: false,
                rectangle: false,
                circle: false,
                marker: false,
                circlemarker: false,
            },
            edit: {
                featureGroup: drawnItemsRef.current,
            }
        });
        map.addControl(drawControl);
        map.on('draw:created', onCreated);
        map.on('draw:deleted', onDeleted);

        return () => {
            map.off('draw:created', onCreated);
            map.off('draw:deleted', onDeleted);
            map.removeControl(drawControl);
        };
    }, [map, onCreated, onDeleted, drawnItemsRef]);

    return null;
};

const CreateChallenge = () => {
    const [form] = Form.useForm();
    const [drawnPolygon, setDrawnPolygon] = useState(null);
    const [map, setMap] = useState(null);
    const drawnItemsRef = useRef(new L.FeatureGroup());

    const { user } = useAuth();

    // Event handler for when a new shape is drawn
    const handleDrawCreated = useCallback((e) => {
        const layer = e.layer;
        drawnItemsRef.current.clearLayers();
        drawnItemsRef.current.addLayer(layer);
        setDrawnPolygon(layer);

        // Fit map to the drawn polygon
        if (map) {
            map.fitBounds(layer.getBounds());
        }
    }, [map]);

    // Event handler for when a drawn shape is deleted
    const handleDrawDeleted = useCallback(() => {
        setDrawnPolygon(null);
    }, []);

    // Callback to recenter and zoom the map when a location is found/selected
    const handleLocationFound = (coordinates) => {
        if (map) {
            // Set a reasonable zoom level for the selected location
            map.setView(coordinates, 15, {
                animate: true,
                duration: 1
            });
        }
    };

    // Handle challenge form submission
    const handleSubmit = async (values) => {
        if (!drawnPolygon) {
            message.error('Please draw a boundary for the challenge');
            return;
        }

        const formData = new FormData();
        formData.append('user_id', user.user_id);
        formData.append('title', values.title);
        formData.append('description', values.description);
        formData.append('boundary', JSON.stringify(drawnPolygon.toGeoJSON().geometry));

        // Ensure the photo is available and use optional chaining as an extra safeguard.
        if (values.photo && values.photo[0] && values.photo[0].originFileObj) {
            formData.append('photo', values.photo[0].originFileObj);
        } else {
            message.error('Photo upload seems to be missing');
            return;
        }

        try {
            await challengeService.createChallenge(formData);
            message.success('Challenge created successfully');
            form.resetFields();
            drawnItemsRef.current.clearLayers();
            setDrawnPolygon(null);
        } catch (error) {
            console.error('Error creating challenge:', error);
            message.error('Failed to create challenge');
        }
    };

    return (
        <div className="container mt-4">
            <h2>Create New Challenge</h2>
            <Form form={form} onFinish={handleSubmit} layout="vertical">
                <Form.Item
                    name="title"
                    label="Title"
                    rules={[{ required: true, message: 'Please enter a title' }]}
                >
                    <Input />
                </Form.Item>

                <Form.Item
                    name="description"
                    label="Description"
                    rules={[{ required: true, message: 'Please enter a description' }]}
                >
                    <Input.TextArea />
                </Form.Item>

                <Form.Item
                    name="photo"
                    label="Photo"
                    valuePropName="fileList"
                    getValueFromEvent={(e) => {
                        // The Upload component returns an event; extract fileList from it.
                        return Array.isArray(e) ? e : e && e.fileList;
                    }}
                    rules={[{ required: true, message: 'Please upload a photo' }]}
                >
                    <Upload
                        listType="picture"
                        beforeUpload={() => false}
                        maxCount={1}
                    >
                        <Button icon={<UploadOutlined />}>Upload Photo</Button>
                    </Upload>
                </Form.Item>

                <div style={{ height: '400px', marginBottom: '20px', position: 'relative' }}>
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
                        <FeatureGroup ref={drawnItemsRef} />
                        <LeafletDrawControl
                            onCreated={handleDrawCreated}
                            onDeleted={handleDrawDeleted}
                            drawnItemsRef={drawnItemsRef}
                        />
                    </MapContainer>
                </div>

                <Form.Item>
                    <Button type="primary" htmlType="submit">
                        Create Challenge
                    </Button>
                </Form.Item>
            </Form>
        </div>
    );
};

export default CreateChallenge;
