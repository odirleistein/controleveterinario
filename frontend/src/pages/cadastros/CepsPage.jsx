import CrudPage from "../../components/CrudPage";
import { formatarCep } from "../../utils/format";

const fields = [
  // O CEP e a chave do registro: so se digita ao criar (ver CepUpdate no backend).
  { name: "cep", label: "CEP", type: "text", required: true, somenteNovo: true },
  {
    name: "localidade_id", label: "Localidade", type: "select", optionsResource: "localidades",
    labelKey: "rotulo", isId: true, required: true,
  },
];

const columns = [
  { key: "cep", label: "CEP", render: (v) => formatarCep(v) },
  { key: "localidade_rotulo", label: "Localidade" },
  { key: "cidade_uf", label: "Cidade", opcional: true },
];

export default function CepsPage() {
  return <CrudPage larga resource="ceps" title="CEPs" fields={fields} columns={columns} campoBusca="cep" />;
}
