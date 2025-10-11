import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000", // backend FastAPI base URL
});

// Attach token automatically if available
API.interceptors.request.use((config) => {
  const auth = localStorage.getItem("auth");
  if (auth) {
    const { token } = JSON.parse(auth);
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default API;
