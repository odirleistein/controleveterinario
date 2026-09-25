import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [registroAberto, setRegistroAberto] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // "Criar conta" so existe enquanto o sistema nao tem nenhum usuario (o primeiro
  // vira MASTER); depois disso quem cadastra e o master, na tela de Usuarios.
  useEffect(() => {
    api
      .get("/auth/registro-aberto")
      .then((res) => setRegistroAberto(res.data.aberto))
      .catch(() => setRegistroAberto(false));
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setErro("");
    setEnviando(true);
    try {
      await login(email, senha);
      navigate(location.state?.from ?? "/dashboard", { replace: true });
    } catch (err) {
      setErro(err.response?.data?.detail ?? "Falha ao entrar. Verifique suas credenciais.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="login-screen">
      <form className="login-card" onSubmit={handleSubmit}>
        <h1>Controle Veterinário</h1>
        <p className="subtitle">Entre com sua conta</p>
        {erro && <div className="alert-error">{erro}</div>}
        <label>
          E-mail
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoFocus
          />
        </label>
        <label>
          Senha
          <input type="password" value={senha} onChange={(e) => setSenha(e.target.value)} required />
        </label>
        <button type="submit" disabled={enviando}>
          {enviando ? "Entrando..." : "Entrar"}
        </button>
        {registroAberto && (
          <Link to="/registrar" className="link-back">
            Primeiro acesso: criar o usuário administrador
          </Link>
        )}
      </form>
    </div>
  );
}
