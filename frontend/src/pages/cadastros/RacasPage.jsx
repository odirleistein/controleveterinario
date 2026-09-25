import CrudPage from "../../components/CrudPage";

const fields = [
  { name: "descricao", label: "Descrição", type: "text", required: true },
  { name: "ativo", label: "Ativo", type: "checkbox", default: true },
];

const columns = [
  { key: "descricao", label: "Raça" },
  { key: "ativo", label: "Situação", render: (v) => (v ? "Ativa" : "Inativa") },
];

export default function RacasPage() {
  return <CrudPage resource="racas" title="Raças" fields={fields} columns={columns} campoBusca="descricao" />;
}
