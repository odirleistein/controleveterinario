import CrudPage from "../components/CrudPage";
import { useAuth } from "../context/AuthContext";

const fields = [
  {
    name: "tipo_animal_id", label: "Tipo", type: "select", optionsResource: "tipos-animal",
    labelKey: "descricao", isId: true, required: true,
    optionsFilter: (t) => t.ativo,
  },
  { name: "nome", label: "Nome", type: "text", required: true },
  { name: "codigo", label: "Código / brinco", type: "text" },
  { name: "ativo", label: "Ativo", type: "checkbox", default: true },
];

const columns = [
  { key: "nome", label: "Animal" },
  { key: "tipo_descricao", label: "Tipo" },
  { key: "codigo", label: "Código", render: (v) => v ?? "-" },
  { key: "ativo", label: "Situação", render: (v) => (v ? "Ativo" : "Inativo") },
];

// Sempre da propriedade aberta: o cabecalho X-Propriedade-Id vai em todo pedido e o
// animal criado aqui ja nasce vinculado a ela.
export default function AnimaisPage() {
  const { propriedade } = useAuth();
  return (
    <CrudPage
      larga
      resource="animais"
      title={`Animais — ${propriedade.nome}`}
      fields={fields}
      columns={columns}
      campoBusca="nome"
    />
  );
}
