import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import { saveLocation, getLocation, isRecipient, getUser } from '../auth';
import { getUserProfile } from '../api';

// Component to handle map clicks
const LocationMarker = ({ position, setPosition }) => {
  const map = useMapEvents({
    click(e) {
      const { lat, lng } = e.latlng;
      setPosition([lat, lng]);
    }
  });

  return position === null ? null : (
    <Marker position={position} />
  );
};

const MapPage = () => {
  const [position, setPosition] = useState(null);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        const userData = await getUserProfile();
        setUser(userData);
        
        // If user already has location, use it
        if (userData.latitude && userData.longitude) {
          setPosition([userData.latitude, userData.longitude]);
        } else {
          // Check if we have location in local storage
          const storedLocation = getLocation();
          if (storedLocation) {
            setPosition([storedLocation.latitude, storedLocation.longitude]);
          }
        }
      } catch (error) {
        console.error('Error fetching user profile:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUserProfile();
  }, []);

  const handleSaveLocation = () => {
    if (position) {
      saveLocation(position[0], position[1]);
      
      // Navigate based on user type
      if (isRecipient()) {
        navigate('/nearby-gatherings');
      } else {
        // For donors, we could navigate to a donor dashboard
        // Currently just show a message
        alert('Location saved! As a donor, you can now create gatherings (not implemented in this demo).');
      }
    } else {
      alert('Please select a location on the map first');
    }
  };

  if (loading) {
    return <div>Loading user data...</div>;
  }

  return (
    <div>
      <h1>Select Your Location</h1>
      <p>Click on the map to set your location.</p>
      
      <div style={{ height: '500px', width: '100%', marginBottom: '20px' }}>
        <MapContainer 
          center={position || [37.7749, -122.4194]} // Default to San Francisco
          zoom={13} 
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          <LocationMarker position={position} setPosition={setPosition} />
        </MapContainer>
      </div>
      
      {position && (
        <div>
          <p>Selected coordinates: {position[0].toFixed(6)}, {position[1].toFixed(6)}</p>
        </div>
      )}
      
      <button 
        onClick={handleSaveLocation} 
        disabled={!position}
        style={{ 
          padding: '10px 20px', 
          fontSize: '16px',
          opacity: position ? 1 : 0.5
        }}
      >
        Save Location & Continue
      </button>
    </div>
  );
};

export default MapPage;