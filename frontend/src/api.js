import axios from "axios";

const API_ROOT = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");
const api = axios.create({ baseURL: `${API_ROOT}/api` });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// If the login token has expired, clear it and send the user to the login page.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && localStorage.getItem("access")) {
      localStorage.removeItem("access");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export const errText = (e) => {
  const data = e.response?.data;
  const d = data?.error ?? data?.detail ?? data;
  if (typeof d === "string") return d;
  if (d?.detail && typeof d.detail === "string") return d.detail;
  if (d && typeof d === "object") {
    return Object.entries(d)
      .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(" ") : String(value)}`)
      .join(" | ");
  }
  return "Network error. Is the backend running?";
};

export default api;