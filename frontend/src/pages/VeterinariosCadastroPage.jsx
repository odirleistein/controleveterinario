import { MapPinned } from "lucide-react";
import { useState } from "react";
import CrudPage from "../components/CrudPage";
import VinculosModal from "../components/VinculosModal";
import { useAuth } from "../context/AuthContext";
import { formatarTelefone } from "../utils/format";

// Cadastro geral (so MASTER): fora do contexto de propriedade.
// Veterinario e so o papel profissional: os dados pessoais (nome, endereco,
// telefones) ficam em Pessoas, e o login em Usuarios.
const fields = [
  {
    name: "pessoa_id", label: "Pessoa (física)", type: "select", optionsResource: "pessoas",
    isId: true, required: true, optionsFilter: (p) => p.ativo && p.tipo_pessoa === "F",
  },
  {
    name: "usuario_id", label: "Usuário (login)", type: "select", optionsResource: "usuarios",
    labelKey: "email", isId: true, required: true, optionsFilter: (u) => u.ativo,
  },
  { name: "ativo", label: "Ativo", type: "checkbox", default: true },
];

const columns = [
  { key: "nome", label: "Veterinário" },
  { key: "usuario_email", label: "Login", opcional: true },
  { key: "telefone_principal", label: "Telefone", render: (v) => (v ? formatarTelefone(v) : "-") },
  { key: "ativo", label: "Situação", render: (v) => (v ? "Ativo" : "Inativo") },
];

export default function VeterinariosCadastroPage() {
  const { podeEscrever } = useAuth();
  const [aberto, setAberto] = useState(null);

  return (
    <>
      <CrudPage
        larga
        resource="veterinarios"
        title="Veterinários"
        fields={fields}
        columns={columns}
        campoBusca="nome"
        extraActions={(veterinario) => (
          <button
            type="button"
            className="icon-btn"
            title="Propriedades que atende"
            onClick={() => setAberto(veterinario)}
          >
            <MapPinned size={15} />
          </button>
        )}
      />
      {aberto && (
        <VinculosModal
          titulo={`Propriedades — ${aberto.nome}`}
          url={`/veterinarios/${aberto.id}/propriedades`}
          resource="propriedades"
          rotulo={(p) => `${p.nome} — ${p.cidade_uf}`}
          somenteLeitura={!podeEscrever}
          onFechar={() => setAberto(null)}
        />
      )}
    </>
  );
}
