import CrudPage from "../../components/CrudPage";
import { formatarData, formatarDocumento, formatarTelefone } from "../../utils/format";

const TIPOS = [
  { value: "F", label: "Física" },
  { value: "J", label: "Jurídica" },
];

const fisica = (d) => d.tipo_pessoa === "F";
const juridica = (d) => d.tipo_pessoa === "J";

const fields = [
  { name: "tipo_pessoa", label: "Tipo", type: "select", options: TIPOS, required: true, default: "F" },
  { name: "nome", label: "Nome", type: "text", required: true },
  // Pessoa fisica
  { name: "cpf", label: "CPF", type: "text", mostrarSe: fisica },
  { name: "data_nascimento", label: "Data de nascimento", type: "date", mostrarSe: fisica },
  // Pessoa juridica
  { name: "razao_social", label: "Razão social", type: "text", mostrarSe: juridica },
  { name: "nome_fantasia", label: "Nome fantasia", type: "text", mostrarSe: juridica },
  { name: "cnpj", label: "CNPJ", type: "text", mostrarSe: juridica },
  { name: "data_fundacao", label: "Data de fundação", type: "date", mostrarSe: juridica },
  { name: "email", label: "E-mail", type: "email" },
  { name: "cep", label: "CEP", type: "cep" },
  { name: "endereco", label: "Endereço", type: "text" },
  { name: "numero", label: "Número", type: "text" },
  { name: "complemento", label: "Complemento", type: "text" },
  { name: "telefones", label: "Telefones", type: "telefones", default: [] },
  { name: "ativo", label: "Ativo", type: "checkbox", default: true },
];

const columns = [
  { key: "nome", label: "Nome" },
  { key: "tipo_pessoa", label: "Tipo", render: (v) => (v === "J" ? "Jurídica" : "Física") },
  { key: "documento", label: "CPF / CNPJ", opcional: true, render: (v) => (v ? formatarDocumento(v) : "-") },
  { key: "email", label: "E-mail", opcional: true },
  { key: "telefone_principal", label: "Telefone", render: (v) => (v ? formatarTelefone(v) : "-") },
  { key: "cidade_uf", label: "Cidade", opcional: true },
  {
    key: "data_nascimento",
    label: "Nascimento",
    opcional: true,
    render: (v) => (v ? formatarData(v) : "-"),
  },
  { key: "ativo", label: "Situação", render: (v) => (v ? "Ativa" : "Inativa") },
];

const filtrosExtras = [{ campo: "tipo_pessoa", label: "Todos os tipos", opcoes: TIPOS }];

export default function PessoasPage() {
  return (
    <CrudPage
      larga
      largo
      resource="pessoas"
      title="Pessoas"
      fields={fields}
      columns={columns}
      campoBusca="nome"
      filtrosExtras={filtrosExtras}
    />
  );
}
