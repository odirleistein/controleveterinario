import CrudPage from "../../components/CrudPage";

const fields = [
  {
    name: "cidade_id", label: "Cidade", type: "select", optionsResource: "cidades", labelKey: "rotulo",
    isId: true, required: true,
  },
  { name: "nome", label: "Nome", type: "text", required: true },
  { name: "ativo", label: "Ativo", type: "checkbox", default: true },
];

const columns = [
  { key: "nome", label: "Bairro" },
  { key: "cidade_rotulo", label: "Cidade" },
  { key: "ativo", label: "Situação", render: (v) => (v ? "Ativo" : "Inativo") },
];

export default function BairrosPage() {
  return (
    <CrudPage larga resource="bairros" title="Bairros" fields={fields} columns={columns} campoBusca="nome" />
  );
}
