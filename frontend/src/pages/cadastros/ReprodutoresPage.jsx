import CrudPage from "../../components/CrudPage";

const SEXOS = [
  { value: "M", label: "Touro (macho)" },
  { value: "F", label: "Vaca (fêmea)" },
];

const fields = [
  { name: "nome", label: "Nome", type: "text", required: true },
  { name: "registro", label: "Registro / código da central", type: "text" },
  { name: "sexo", label: "Sexo", type: "select", options: SEXOS, required: true },
  {
    name: "raca_id", label: "Raça", type: "select", optionsResource: "racas",
    labelKey: "descricao", isId: true, optionsFilter: (r) => r.ativo,
  },
  { name: "empresa", label: "Empresa (central de sêmen)", type: "text" },
  {
    name: "pai_id", label: "Pai", type: "select", optionsResource: "reprodutores",
    labelKey: "nome", isId: true, optionsFilter: (r) => r.ativo && r.sexo === "M",
  },
  {
    name: "mae_id", label: "Mãe", type: "select", optionsResource: "reprodutores",
    labelKey: "nome", isId: true, optionsFilter: (r) => r.ativo && r.sexo === "F",
  },
  { name: "ativo", label: "Ativo", type: "checkbox", default: true },
];

const columns = [
  { key: "nome", label: "Reprodutor" },
  { key: "sexo", label: "Sexo", render: (v) => (v === "M" ? "Touro" : "Vaca") },
  { key: "raca_descricao", label: "Raça", render: (v) => v ?? "-" },
  { key: "empresa", label: "Empresa", opcional: true, render: (v) => v ?? "-" },
  { key: "pai_nome", label: "Pai", opcional: true, render: (v) => v ?? "-" },
  { key: "mae_nome", label: "Mãe", opcional: true, render: (v) => v ?? "-" },
  { key: "ativo", label: "Situação", render: (v) => (v ? "Ativo" : "Inativo") },
];

// Cadastro geral (vale para todas as propriedades): touros e vacas que aparecem como pai,
// mae ou touro de inseminacao. Avos e bisavos saem da cadeia pai/mae de cada um.
export default function ReprodutoresPage() {
  return (
    <CrudPage
      larga
      largo
      resource="reprodutores"
      title="Reprodutores (genealogia)"
      fields={fields}
      columns={columns}
      campoBusca="nome"
    />
  );
}
