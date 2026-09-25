import CrudPage from "../../components/CrudPage";

// Sub-area da cidade (na zona rural: a linha, o distrito, a comunidade). Nao fica
// dentro de um bairro: bairro e localidade sao cadastros paralelos da cidade.
const fields = [
  {
    name: "cidade_id", label: "Cidade", type: "select", optionsResource: "cidades", labelKey: "rotulo",
    isId: true, required: true,
  },
  { name: "nome", label: "Nome", type: "text", required: true },
  { name: "ativa", label: "Ativa", type: "checkbox", default: true },
];

const columns = [
  { key: "nome", label: "Localidade" },
  { key: "cidade_rotulo", label: "Cidade" },
  { key: "ativa", label: "Situação", render: (v) => (v ? "Ativa" : "Inativa") },
];

export default function LocalidadesPage() {
  return (
    <CrudPage larga resource="localidades" title="Localidades" fields={fields} columns={columns} campoBusca="nome" />
  );
}
