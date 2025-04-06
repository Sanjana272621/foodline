import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getNearbyGatherings, getAllGatherings, claimGathering } from '../api';
import { getLocation } from '../auth';

const NearbyGatheringsPage = () => {
  const [gatherings, setGatherings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchGatherings = async () => {
      try {
        setLoading(true);
        const location = getLocation();
        
        if (!location || !location.latitude || !location.longitude) {
          navigate('/map');
          return;
        }
        
        let data;
        try {
          // Try to get nearby gatherings first
          data = await getNearbyGatherings(location.latitude, location.longitude);
        } catch (err) {
          // Fallback to all gatherings if nearby endpoint fails
          console.log('Falling back to all gatherings');
          data = await getAllGatherings();
        }
        
        setGatherings(data);
      } catch (err) {
        console.error('Error fetching gatherings:', err);
        setError('Failed to load gatherings. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchGatherings();
  }, [navigate]);

  const handleClaim = async (gatheringId) => {
    try {
      await claimGathering(gatheringId);
      
      // Update the gatherings list to mark this one as claimed
      setGatherings(gatherings.map(g => 
        g.id === gatheringId ? { ...g, is_taken: true } : g
      ));
      
      alert('Food claimed successfully! The donor will be notified.');
    } catch (err) {
      console.error('Error claiming gathering:', err);
      alert('Failed to claim food. It may have already been claimed.');
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const goBack = () => {
    navigate('/map');
  };

  if (loading) {
    return <div>Loading gatherings...</div>;
  }

  return (
    <div>
      <h1>Nearby Food Gatherings</h1>
      <button onClick={goBack} style={{ marginBottom: '20px' }}>
        Back to Map
      </button>
      
      {error && <div style={{ color: 'red', marginBottom: '15px' }}>{error}</div>}
      
      {gatherings.length === 0 ? (
        <p>No available food gatherings found nearby.</p>
      ) : (
        <div>
          {gatherings
            .filter(g => !g.is_taken) // Only show unclaimed gatherings
            .map(gathering => (
              <div key={gathering.id} className="card">
                <h3>{gathering.food_details}</h3>
                <p>
                  <strong>Available from:</strong> {formatDate(gathering.available_from)}
                </p>
                <p>
                  <strong>Available until:</strong> {formatDate(gathering.available_to)}
                </p>
                <p>
                  <strong>Location:</strong> Approx. {
                    gathering.distance ? 
                    `${gathering.distance.toFixed(2)} km away` : 
                    'Distance not available'
                  }
                </p>
                <button 
                  onClick={() => handleClaim(gathering.id)}
                  style={{ backgroundColor: '#f39c12' }}
                >
                  Claim This Food
                </button>
              </div>
            ))}
        </div>
      )}
    </div>
  );
};

export default NearbyGatheringsPage;