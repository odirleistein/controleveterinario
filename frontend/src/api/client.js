import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8082",
  // Lista vira ?tipo_id=1&tipo_id=2 (o FastAPI nao le o "tipo_id[]" padrao do axios).
  paramsSerializer: { indexes: null },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const rotaAtual = window.location.pathname;
    if (error.response?.status === 401 && rotaAtual !== "/login") {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

export default api;
