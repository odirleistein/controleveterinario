import CrudPage from "../../components/CrudPage";
import { formatarCep } from "../../utils/format";

// Em cidade pequena todos os enderecos dividem o mesmo CEP: por isso um CEP
// escolhe a cidade e, se quiser, varios bairros e varias localidades dela.
const daCidade = (o, dados) => String(o.cidade_id) === String(dados.cidade_id);

const fields = [
  // O CEP e a chave do registro: so se digita ao criar (ver CepUpdate no backend).
  { name: "cep", label: "CEP", type: "text", required: true, somenteNovo: true },
  {
    name: "cidade_id", label: "Cidade", type: "select", optionsResource: "cidades", labelKey: "rotulo",
    isId: true, required: true, limpaAoMudar: ["bairro_ids", "localidade_ids"],
  },
  {
    name: "bairro_ids", label: "Bairros que usam este CEP", type: "multiselect", optionsResource: "bairros",
    optionsFilter: daCidade, nomeMultiplo: "bairros",
    mostrarSe: (d) => Boolean(d.cidade_id),
  },
  {
    name: "localidade_ids", label: "Localidades que usam este CEP", type: "multiselect",
    optionsResource: "localidades", optionsFilter: daCidade, nomeMultiplo: "localidades",
    mostrarSe: (d) => Boolean(d.cidade_id),
  },
];

const columns = [
  { key: "cep", label: "CEP", render: (v) => formatarCep(v) },
  { key: "cidade_uf", label: "Cidade" },
  { key: "bairros_nomes", label: "Bairros", opcional: true, render: (v) => v || "-" },
  { key: "localidades_nomes", label: "Localidades", opcional: true, render: (v) => v || "-" },
];

export default function CepsPage() {
  return <CrudPage larga largo resource="ceps" title="CEPs" fields={fields} columns={columns} campoBusca="cep" />;
}
