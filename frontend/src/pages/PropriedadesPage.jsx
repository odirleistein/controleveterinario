import { Stethoscope, UserCheck } from "lucide-react";
import { useState } from "react";
import CrudPage from "../components/CrudPage";
import VinculosModal from "../components/VinculosModal";
import { useAuth } from "../context/AuthContext";
import { formatarCep } from "../utils/format";

const fields = [
  { name: "nome", label: "Nome da propriedade", type: "text", required: true },
  {
    name: "proprietario_pessoa_id", label: "Proprietário", type: "select", optionsResource: "pessoas",
    isId: true, required: true, optionsFilter: (p) => p.ativo,
  },
  { name: "cep", label: "CEP", type: "cep", required: true },
  { name: "endereco", label: "Endereço", type: "text" },
  { name: "numero", label: "Número", type: "text" },
  { name: "complemento", label: "Complemento", type: "text" },
  { name: "ativa", label: "Ativa", type: "checkbox", default: true },
];

const columns = [
  { key: "nome", label: "Propriedade" },
  { key: "proprietario_nome", label: "Proprietário" },
  { key: "cidade_uf", label: "Cidade" },
  { key: "cep", label: "CEP", opcional: true, render: (v) => formatarCep(v) },
  { key: "ativa", label: "Situação", render: (v) => (v ? "Ativa" : "Inativa") },
];

// O que cada botao da linha abre: quem atende e quem acessa a propriedade. Os animais
// nao entram aqui: cada um nasce dentro da propriedade (tela Animais).
const VINCULOS = [
  {
    chave: "veterinarios", titulo: "Veterinários", Icone: Stethoscope, resource: "veterinarios",
    listaUrl: "/veterinarios/candidatos",
    rotulo: (v) => v.nome,
  },
  {
    chave: "usuarios", titulo: "Usuários com acesso", Icone: UserCheck, resource: "usuarios",
    rotulo: (u) => `${u.nome} — ${u.email}`,
  },
];

export default function PropriedadesPage() {
  const { podeEscrever } = useAuth();
  const [aberto, setAberto] = useState(null); // { propriedade, vinculo }

  return (
    <>
      <CrudPage
        larga
        resource="propriedades"
        title="Propriedades"
        fields={fields}
        columns={columns}
        campoBusca="nome"
        extraActions={(propriedade) =>
          VINCULOS.map((v) => (
            <button
              key={v.chave}
              type="button"
              className="icon-btn"
              title={v.titulo}
              onClick={() => setAberto({ propriedade, vinculo: v })}
            >
              <v.Icone size={15} />
            </button>
          ))
        }
      />
      {aberto && (
        <VinculosModal
          titulo={`${aberto.vinculo.titulo} — ${aberto.propriedade.nome}`}
          url={`/propriedades/${aberto.propriedade.id}/${aberto.vinculo.chave}`}
          resource={aberto.vinculo.resource}
          listaUrl={aberto.vinculo.listaUrl}
          rotulo={aberto.vinculo.rotulo}
          somenteLeitura={!podeEscrever}
          onFechar={() => setAberto(null)}
        />
      )}
    </>
  );
}
