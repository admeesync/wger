// Dynamically resolve the backend API URL based on environment
const getApiBase = () => {
  // If running via file protocol (direct double-click on html file)
  if (window.location.protocol === 'file:') {
    return 'http://localhost:9000/api';
  }
  // If running locally (localhost/127.0.0.1) but on a different port than backend (9000), e.g., Live Server
  if ((window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') && window.location.port !== '9000') {
    return 'http://localhost:9000/api';
  }
  // If running on the Vercel production frontend domain, connect to the Render production backend
  if (window.location.hostname === 'wger-mu.vercel.app') {
    return 'https://wger-h9qn.onrender.com/api';
  }
  // In production (or when served from backend on port 9000), use current host/port
  return `${window.location.origin}/api`;
};

const API_BASE = getApiBase();
