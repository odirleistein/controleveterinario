import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/client";

export default function Registrar() {
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");
  const [sucesso, setSucesso] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setErro("");
    setEnviando(true);
    try {
      await api.post("/auth/registrar", { nome, email, senha });
      setSucesso(true);
      setTimeout(() => navigate("/login"), 1200);
    } catch (err) {
      setErro(err.response?.data?.detail ?? "Erro ao criar conta.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="login-screen">
      <form className="login-card" onSubmit={handleSubmit}>
        <h1>Primeiro acesso</h1>
        <p className="subtitle">Crie o usuário administrador (master) do sistema</p>
        {erro && <div className="alert-error">{erro}</div>}
        {sucesso && <div className="alert-success">Usuário criado! Redirecionando para o login...</div>}
        <label>
          Nome
          <input type="text" value={nome} onChange={(e) => setNome(e.target.value)} required autoFocus />
        </label>
        <label>
          E-mail
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          Senha (mínimo 8 caracteres)
          <input
            type="password"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            required
            minLength={8}
          />
        </label>
        <button type="submit" disabled={enviando}>
          {enviando ? "Criando..." : "Criar administrador"}
        </button>
        <Link to="/login" className="link-back">
          Voltar ao login
        </Link>
      </form>
    </div>
  );
}
