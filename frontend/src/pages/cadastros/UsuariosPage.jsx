import { KeyRound } from "lucide-react";
import { useState } from "react";
import api from "../../api/client";
import CrudPage from "../../components/CrudPage";
import { mensagemErro } from "../../utils/erros";

const fields = [
  { name: "nome", label: "Nome", type: "text", required: true },
  { name: "email", label: "E-mail", type: "email", required: true },
  // Senha so no cadastro: para trocar depois existe o botao "Redefinir senha".
  { name: "senha", label: "Senha (mínimo 8 caracteres)", type: "password", required: true, somenteNovo: true },
  { name: "papel_id", label: "Papel", type: "select", optionsResource: "papeis", isId: true, required: true },
  // Vincula o login a identidade real da pessoa; fica vazio para contas de servico.
  {
    name: "pessoa_id", label: "Pessoa (opcional)", type: "select", optionsResource: "pessoas",
    isId: true, optionsFilter: (p) => p.ativo,
  },
  { name: "ativo", label: "Ativo", type: "checkbox", default: true },
];

const columns = [
  { key: "nome", label: "Nome" },
  { key: "email", label: "E-mail" },
  { key: "papel_nome", label: "Papel" },
  { key: "ativo", label: "Ativo", render: (v) => (v ? "Sim" : "Não") },
  {
    key: "data_inclusao", opcional: true,
    label: "Criado em",
    render: (v) => (v ? new Date(v).toLocaleDateString("pt-BR") : "-"),
  },
];

function RedefinirSenhaButton({ usuario }) {
  const [aberto, setAberto] = useState(false);
  const [novaSenha, setNovaSenha] = useState("");
  const [confirmacao, setConfirmacao] = useState("");
  const [erro, setErro] = useState("");
  const [sucesso, setSucesso] = useState(false);
  const [salvando, setSalvando] = useState(false);

  function fechar() {
    setAberto(false);
    setNovaSenha("");
    setConfirmacao("");
    setErro("");
    setSucesso(false);
  }

  async function salvar(e) {
    e.preventDefault();
    if (novaSenha !== confirmacao) {
      setErro("As senhas não conferem.");
      return;
    }
    setSalvando(true);
    setErro("");
    try {
      await api.patch(`/usuarios/${usuario.id}/senha`, { nova_senha: novaSenha });
      setSucesso(true);
      setTimeout(fechar, 1200);
    } catch (err) {
      setErro(mensagemErro(err, "Erro ao redefinir a senha."));
    } finally {
      setSalvando(false);
    }
  }

  return (
    <>
      <button type="button" className="icon-btn" title="Redefinir senha" onClick={() => setAberto(true)}>
        <KeyRound size={15} />
      </button>
      {aberto && (
        <div className="modal-backdrop">
          <form className="modal" onSubmit={salvar}>
            <h3>Redefinir senha — {usuario.nome}</h3>
            {erro && <div className="alert-error">{erro}</div>}
            {sucesso && <div className="alert-success">Senha redefinida.</div>}
            <label>
              Nova senha
              <input
                type="password"
                value={novaSenha}
                onChange={(e) => setNovaSenha(e.target.value)}
                minLength={8}
                required
                autoFocus
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
              <button type="button" className="btn-secondary" onClick={fechar}>
                Cancelar
              </button>
              <button type="submit" disabled={salvando}>
                {salvando ? "Salvando..." : "Redefinir"}
              </button>
            </div>
          </form>
        </div>
      )}
    </>
  );
}

export default function UsuariosPage() {
  return (
    <CrudPage
      larga
      resource="usuarios"
      title="Usuários"
      fields={fields}
      columns={columns}
      campoBusca="nome"
      extraActions={(usuario) => <RedefinirSenhaButton usuario={usuario} />}
    />
  );
}
