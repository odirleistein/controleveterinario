import CrudPage from "../../components/CrudPage";

// Sub-area de um bairro; na zona rural e a linha, o distrito ou a comunidade.
const fields = [
  {
    name: "bairro_id", label: "Bairro", type: "select", optionsResource: "bairros", labelKey: "rotulo",
    isId: true, required: true,
  },
  { name: "nome", label: "Nome", type: "text", required: true },
  { name: "ativa", label: "Ativa", type: "checkbox", default: true },
];

const columns = [
  { key: "nome", label: "Localidade" },
  { key: "bairro_rotulo", label: "Bairro" },
  { key: "ativa", label: "Situação", render: (v) => (v ? "Ativa" : "Inativa") },
];

export default function LocalidadesPage() {
  return (
    <CrudPage larga resource="localidades" title="Localidades" fields={fields} columns={columns} campoBusca="nome" />
  );
}
