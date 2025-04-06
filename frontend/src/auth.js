// Local storage keys
const TOKEN_KEY = 'food_donation_token';
const USER_KEY = 'food_donation_user';

// Store authentication token
export const setToken = (token) => {
  localStorage.setItem(TOKEN_KEY, token);
};

// Get authentication token
export const getToken = () => {
  return localStorage.getItem(TOKEN_KEY);
};

// Remove token (logout)
export const removeToken = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
};

// Store user data
export const setUser = (user) => {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

// Get user data
export const getUser = () => {
  const user = localStorage.getItem(USER_KEY);
  return user ? JSON.parse(user) : null;
};

// Check if user is authenticated
export const isAuthenticated = () => {
  return !!getToken();
};

// Check if user is a donor
export const isDonor = () => {
  const user = getUser();
  return user && user.user_type === 'donor';
};

// Check if user is a recipient
export const isRecipient = () => {
  const user = getUser();
  return user && user.user_type === 'recipient';
};

// Save user location
export const saveLocation = (latitude, longitude) => {
  const user = getUser();
  if (user) {
    user.latitude = latitude;
    user.longitude = longitude;
    setUser(user);
  }
};

// Get user location
export const getLocation = () => {
  const user = getUser();
  if (user && user.latitude && user.longitude) {
    return { latitude: user.latitude, longitude: user.longitude };
  }
  return null;
};