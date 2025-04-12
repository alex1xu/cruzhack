import React, { useState } from 'react';
import { AutoComplete, message } from 'antd';

const LocationSearch = ({ onLocationFound }) => {
    const [options, setOptions] = useState([]);

    // Fetch suggestions from Nominatim as the user types.
    const handleSearch = async (value) => {
        if (!value.trim()) {
            setOptions([]);
            return;
        }
        try {
            const response = await fetch(
                `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(value)}`
            );
            const data = await response.json();
            if (data.length > 0) {
                const newOptions = data.map((item) => ({
                    value: item.display_name,
                    lat: parseFloat(item.lat),
                    lon: parseFloat(item.lon)
                }));
                setOptions(newOptions);
            } else {
                setOptions([]);
                message.warning('No location found');
            }
        } catch (error) {
            console.error('Search error:', error);
            message.error('Failed to search location');
        }
    };

    // When a suggestion is selected, call onLocationFound with coordinates.
    const onSelect = (value, option) => {
        console.log('Selected location:', option);
        onLocationFound([option.lat, option.lon]);
    };

    return (
        <AutoComplete
            options={options}
            style={{ width: 300 }}
            onSearch={handleSearch}
            onSelect={onSelect}
            placeholder="Search location..."
            filterOption={false}
        />
    );
};

export default LocationSearch;
