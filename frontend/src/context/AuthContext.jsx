import { createContext, useCallback, useContext, useEffect, useState } from "react";
import api, { definirPropriedadeAtual } from "../api/client";

const AuthContext = createContext(null);

// Nomes dos papeis semeados no banco (tabela papeis).
const MASTER = "MASTER";
const ADMIN = "ADMIN";

const CHAVE_PROPRIEDADE = "propriedade_id";

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [propriedades, setPropriedades] = useState([]);
  const [propriedade, setPropriedade] = useState(null);
  const [carregando, setCarregando] = useState(true);

  /**
   * Carrega as propriedades a que o usuario tem acesso e abre a que ele ja tinha
   * escolhido. Se a escolha anterior nao vale mais (acesso removido, propriedade
   * inativada), descarta. Quem tem uma propriedade so entra direto nela - nao ha
   * o que escolher; com varias, a tela de escolha assume.
   */
  const carregarPropriedades = useCallback(async () => {
    const res = await api.get("/propriedades/");
    const ativas = res.data.filter((p) => p.ativa);
    setPropriedades(ativas);

    const salva = Number(localStorage.getItem(CHAVE_PROPRIEDADE));
    const escolhida = ativas.find((p) => p.id === salva) ?? (ativas.length === 1 ? ativas[0] : null);
    if (escolhida) {
      localStorage.setItem(CHAVE_PROPRIEDADE, String(escolhida.id));
      definirPropriedadeAtual(escolhida.id);
    } else {
      localStorage.removeItem(CHAVE_PROPRIEDADE);
      definirPropriedadeAtual(null);
    }
    setPropriedade(escolhida);
  }, []);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      setCarregando(false);
      return;
    }
    definirPropriedadeAtual(Number(localStorage.getItem(CHAVE_PROPRIEDADE)) || null);
    api
      .get("/auth/me")
      .then(async (res) => {
        setUsuario(res.data);
        await carregarPropriedades();
      })
      .catch(() => localStorage.removeItem("token"))
      .finally(() => setCarregando(false));
  }, [carregarPropriedades]);

  async function login(email, senha) {
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", senha);
    const res = await api.post("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    localStorage.setItem("token", res.data.access_token);
    // Um acesso novo comeca pela escolha da propriedade, nao pela ultima usada.
    localStorage.removeItem(CHAVE_PROPRIEDADE);
    definirPropriedadeAtual(null);
    const me = await api.get("/auth/me");
    setUsuario(me.data);
    await carregarPropriedades();
  }

  /**
   * Abre uma propriedade. Recarrega a pagina de proposito: cada tela guarda a
   * propria lista em memoria, e sem o recarregamento ficariam mostrando dados
   * da propriedade anterior ate alguem navegar de novo.
   */
  function escolherPropriedade(id) {
    const escolhida = propriedades.find((p) => p.id === Number(id));
    if (!escolhida) return;
    localStorage.setItem(CHAVE_PROPRIEDADE, String(escolhida.id));
    window.location.assign("/dashboard");
  }

  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem(CHAVE_PROPRIEDADE);
    definirPropriedadeAtual(null);
    setUsuario(null);
    setPropriedade(null);
    setPropriedades([]);
  }

  // Espelha as regras do backend (security.py) so para esconder o que o usuario
  // nao pode usar; quem barra de verdade e a API.
  const papel = usuario?.papel_nome;
  const ehMaster = papel === MASTER;
  const podeEscrever = papel === MASTER || papel === ADMIN;

  return (
    <AuthContext.Provider
      value={{
        usuario, propriedade, propriedades, carregando, login, logout,
        escolherPropriedade, ehMaster, podeEscrever,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
