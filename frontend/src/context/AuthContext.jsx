import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/client";

const AuthContext = createContext(null);

// Nomes dos papeis semeados no banco (tabela papeis).
const MASTER = "MASTER";
const ADMIN = "ADMIN";

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      setCarregando(false);
      return;
    }
    api
      .get("/auth/me")
      .then((res) => setUsuario(res.data))
      .catch(() => localStorage.removeItem("token"))
      .finally(() => setCarregando(false));
  }, []);

  async function login(email, senha) {
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", senha);
    const res = await api.post("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    localStorage.setItem("token", res.data.access_token);
    const me = await api.get("/auth/me");
    setUsuario(me.data);
  }

  function logout() {
    localStorage.removeItem("token");
    setUsuario(null);
  }

  // Espelha as regras do backend (security.py) so para esconder o que o usuario
  // nao pode usar; quem barra de verdade e a API.
  const papel = usuario?.papel_nome;
  const ehMaster = papel === MASTER;
  const podeEscrever = papel === MASTER || papel === ADMIN;

  return (
    <AuthContext.Provider value={{ usuario, carregando, login, logout, ehMaster, podeEscrever }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
