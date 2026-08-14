import axios from 'axios';

// Vite exposes env vars on import.meta.env; use VITE_API_URL for the backend base URL
const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL });

export default api;
