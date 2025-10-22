import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api", // ✅ matches your FastAPI route prefix
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;
