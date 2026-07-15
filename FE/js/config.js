// Only line you need to change when deploying FE to a different server than BE.
const API_BASE = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost'
    ? 'http://127.0.0.1:8000/api'
    : 'https://wger-rwkr.onrender.com/api';

