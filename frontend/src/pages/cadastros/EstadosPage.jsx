import CrudPage from "../../components/CrudPage";

const fields = [
  { name: "nome", label: "Nome", type: "text", required: true },
  { name: "sigla", label: "Sigla (UF)", type: "text", required: true },
];

const columns = [
  { key: "nome", label: "Estado" },
  { key: "sigla", label: "UF" },
];

export default function EstadosPage() {
  return <CrudPage resource="estados" title="Estados" fields={fields} columns={columns} campoBusca="nome" />;
}
