import { useState } from "react";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";
import { mensagemErro } from "../utils/erros";

export default function MinhaContaPage() {
  const { usuario } = useAuth();
  const [senhaAtual, setSenhaAtual] = useState("");
  const [novaSenha, setNovaSenha] = useState("");
  const [confirmacao, setConfirmacao] = useState("");
  const [erro, setErro] = useState("");
  const [sucesso, setSucesso] = useState(false);
  const [salvando, setSalvando] = useState(false);

  async function salvar(e) {
    e.preventDefault();
    setErro("");
    setSucesso(false);
    if (novaSenha !== confirmacao) {
      setErro("A confirmação não confere com a nova senha.");
      return;
    }
    if (novaSenha === senhaAtual) {
      setErro("A nova senha precisa ser diferente da atual.");
      return;
    }
    setSalvando(true);
    try {
      await api.post("/auth/alterar-senha", { senha_atual: senhaAtual, nova_senha: novaSenha });
      setSucesso(true);
      setSenhaAtual("");
      setNovaSenha("");
      setConfirmacao("");
    } catch (err) {
      setErro(mensagemErro(err, "Erro ao alterar a senha."));
    } finally {
      setSalvando(false);
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <h2>Minha conta</h2>
      </div>

      <div className="card">
        <dl className="dados-conta">
          <dt>Nome</dt>
          <dd>{usuario?.nome ?? "-"}</dd>
          <dt>E-mail</dt>
          <dd>{usuario?.email ?? "-"}</dd>
        </dl>
        <p className="empty-inline">
          Para alterar nome ou e-mail, use a tela de Usuários.
        </p>
      </div>

      <div className="card">
        <h3>Alterar senha</h3>
        {erro && <div className="alert-error">{erro}</div>}
        {sucesso && <div className="alert-success">Senha alterada com sucesso.</div>}
        <form className="form-estreito" onSubmit={salvar}>
          <label>
            Senha atual
            <input
              type="password"
              value={senhaAtual}
              onChange={(e) => setSenhaAtual(e.target.value)}
              required
            />
          </label>
          <label>
            Nova senha (mínimo 8 caracteres)
            <input
              type="password"
              value={novaSenha}
              onChange={(e) => setNovaSenha(e.target.value)}
              minLength={8}
              required
            />
          </label>
          <label>
            Confirmar nova senha
            <input
              type="password"
              value={confirmacao}
              onChange={(e) => setConfirmacao(e.target.value)}
              minLength={8}
              required
            />
          </label>
          <div className="modal-actions">
            <button type="submit" disabled={salvando}>
              {salvando ? "Salvando..." : "Alterar senha"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
