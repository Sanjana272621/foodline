import axios from 'axios';
import { getToken } from './auth';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL
});

// Add Authorization header for protected routes
api.interceptors.request.use(config => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const login = async (email, password) => {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  
  const response = await api.post('/users/token', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  });
  return response.data;
};

export const register = async (userData) => {
  const response = await api.post('/users/register', userData);
  return response.data;
};

export const getUserProfile = async () => {
  const response = await api.get('/users/me');
  return response.data;
};

export const getNearbyGatherings = async (latitude, longitude) => {
  const response = await api.get(`/gatherings/nearby?latitude=${latitude}&longitude=${longitude}`);
  return response.data;
};

export const getAllGatherings = async () => {
  const response = await api.get('/gatherings/');
  return response.data;
};

export const claimGathering = async (gatheringId) => {
  const response = await api.post('/claims/', { gathering_id: gatheringId });
  return response.data;
};

export default api;