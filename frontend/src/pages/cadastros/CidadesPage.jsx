import CrudPage from "../../components/CrudPage";

const fields = [
  { name: "estado_id", label: "Estado", type: "select", optionsResource: "estados", isId: true, required: true },
  { name: "nome", label: "Nome", type: "text", required: true },
  { name: "codigo_ibge", label: "Código IBGE", type: "number" },
  { name: "ativa", label: "Ativa", type: "checkbox", default: true },
];

const columns = [
  { key: "nome", label: "Cidade" },
  { key: "estado_sigla", label: "UF" },
  { key: "codigo_ibge", label: "IBGE", opcional: true },
  { key: "ativa", label: "Situação", render: (v) => (v ? "Ativa" : "Inativa") },
];

export default function CidadesPage() {
  return (
    <CrudPage larga resource="cidades" title="Cidades" fields={fields} columns={columns} campoBusca="nome" />
  );
}
