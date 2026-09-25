import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8082",
  // Lista vira ?propriedade_id=1&propriedade_id=2 (o FastAPI nao le o "propriedade_id[]" padrao do axios).
  paramsSerializer: { indexes: null },
});

// Propriedade aberta na tela. Vai em todo pedido; o backend recusa (403) se o
// usuario nao tiver acesso a ela - o recorte de dados de verdade e la.
let propriedadeAtual = null;

export function definirPropriedadeAtual(id) {
  propriedadeAtual = id || null;
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  if (propriedadeAtual) {
    config.headers["X-Propriedade-Id"] = String(propriedadeAtual);
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
