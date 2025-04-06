import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/loginPage'; //using lower case works
import MapPage from './pages/mapPage';
import NearbyGatheringsPage from './pages/nearbyGatheringsPage';
import { isAuthenticated, isRecipient } from './auth';

// Protected route component
const ProtectedRoute = ({ children, allowedRoles = null }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  
  // If roles are specified, check if user has one of the allowed roles
  if (allowedRoles && Array.isArray(allowedRoles)) {
    const hasRole = allowedRoles.some(role => {
      if (role === 'recipient') return isRecipient();
      return false;
    });
    
    if (!hasRole) {
      return <Navigate to="/map" replace />;
    }
  }
  
  return children;
};

function App() {
  return (
    <div className="container">
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/map" element={
          <ProtectedRoute>
            <MapPage />
          </ProtectedRoute>
        } />
        <Route path="/nearby-gatherings" element={
          <ProtectedRoute allowedRoles={['recipient']}>
            <NearbyGatheringsPage />
          </ProtectedRoute>
        } />
        <Route path="/" element={<Navigate to="/login" replace />} />
      </Routes>
    </div>
  );
}

export default App;