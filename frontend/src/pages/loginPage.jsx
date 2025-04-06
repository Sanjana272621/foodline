import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { login, register } from '../api';
import { setToken, setUser, isAuthenticated } from '../auth';

const LoginPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [userType, setUserType] = useState('recipient');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    // Redirect if already logged in
    if (isAuthenticated()) {
      navigate('/map');
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      if (isLogin) {
        // Handle login
        const data = await login(email, password);
        setToken(data.access_token);
        
        // Get user data from token or fetch user profile
        const user = {
          email,
          user_type: data.user_type || 'unknown' // You might need to adjust based on your API response
        };
        setUser(user);
      } else {
        // Handle registration
        if (!name || !email || !password || !userType) {
          setError('All fields are required');
          return;
        }
        
        const userData = {
          name,
          email,
          password,
          user_type: userType,
          // We'll set location later in the Map page
          latitude: 0,
          longitude: 0
        };
        
        const user = await register(userData);
        setUser(user);
        
        // After registration, log in automatically
        const loginData = await login(email, password);
        setToken(loginData.access_token);
      }
      
      // Redirect to map page
      navigate('/map');
    } catch (err) {
      console.error('Authentication error:', err);
      setError(err.response?.data?.detail || 'Authentication failed');
    }
  };

  const toggleForm = () => {
    setIsLogin(!isLogin);
    setError('');
  };

  return (
    <div style={{ maxWidth: '400px', margin: '50px auto' }}>
      <h1>{isLogin ? 'Login' : 'Sign Up'}</h1>
      
      {error && <div style={{ color: 'red', marginBottom: '15px' }}>{error}</div>}
      
      <form onSubmit={handleSubmit}>
        {!isLogin && (
          <div className="form-control">
            <label htmlFor="name">Name:</label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              style={{ width: '100%' }}
            />
          </div>
        )}
        
        <div className="form-control">
          <label htmlFor="email">Email:</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{ width: '100%' }}
          />
        </div>
        
        <div className="form-control">
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ width: '100%' }}
          />
        </div>
        
        {!isLogin && (
          <div className="form-control">
            <label htmlFor="userType">Role:</label>
            <select
              id="userType"
              value={userType}
              onChange={(e) => setUserType(e.target.value)}
              style={{ width: '100%' }}
            >
              <option value="donor">Donor</option>
              <option value="recipient">Recipient</option>
            </select>
          </div>
        )}
        
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <button type="submit" style={{ width: '48%' }}>
            {isLogin ? 'Login' : 'Sign Up'}
          </button>
          <button 
            type="button" 
            onClick={toggleForm} 
            style={{ width: '48%', backgroundColor: '#666' }}
          >
            {isLogin ? 'Switch to Sign Up' : 'Switch to Login'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default LoginPage;