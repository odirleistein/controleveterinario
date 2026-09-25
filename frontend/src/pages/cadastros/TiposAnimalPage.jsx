import CrudPage from "../../components/CrudPage";

const fields = [
  { name: "descricao", label: "Descrição", type: "text", required: true },
  { name: "ativo", label: "Ativo", type: "checkbox", default: true },
];

const columns = [
  { key: "descricao", label: "Tipo de animal" },
  { key: "ativo", label: "Situação", render: (v) => (v ? "Ativo" : "Inativo") },
];

export default function TiposAnimalPage() {
  return (
    <CrudPage resource="tipos-animal" title="Tipos de Animal" fields={fields} columns={columns} campoBusca="descricao" />
  );
}
