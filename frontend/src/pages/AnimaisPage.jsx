import { useEffect, useState } from "react";
import api from "../api/client";
import CrudPage from "../components/CrudPage";
import { useAuth } from "../context/AuthContext";
import { formatarData } from "../utils/format";

const fields = [
  {
    name: "tipo_animal_id", label: "Tipo", type: "select", optionsResource: "tipos-animal",
    labelKey: "descricao", isId: true, required: true,
    optionsFilter: (t) => t.ativo,
  },
  {
    name: "raca_id", label: "Raça", type: "select", optionsResource: "racas",
    labelKey: "descricao", isId: true,
    optionsFilter: (r) => r.ativo,
  },
  { name: "nome", label: "Nome", type: "text", required: true },
  { name: "codigo", label: "Código / brinco", type: "text" },
  { name: "data_nascimento", label: "Data de nascimento", type: "date" },
  { name: "ativo", label: "Ativo", type: "checkbox", default: true },
];

const columns = [
  { key: "nome", label: "Animal" },
  { key: "tipo_descricao", label: "Tipo" },
  { key: "raca_descricao", label: "Raça", render: (v) => v ?? "-" },
  { key: "codigo", label: "Código", render: (v) => v ?? "-" },
  { key: "data_nascimento", label: "Nascimento", render: (v) => (v ? formatarData(v) : "-") },
  { key: "ativo", label: "Situação", render: (v) => (v ? "Ativo" : "Inativo") },
];

// Sempre da propriedade aberta: o cabecalho X-Propriedade-Id vai em todo pedido e o
// animal criado aqui ja nasce vinculado a ela.
export default function AnimaisPage() {
  const { propriedade } = useAuth();
  const [tipos, setTipos] = useState([]);

  // O filtro por tipo lista todos os tipos (inclusive inativos): um animal antigo
  // ainda pode ser de um tipo que ja foi desativado.
  useEffect(() => {
    api.get("/tipos-animal/").then((res) => setTipos(res.data));
  }, []);

  const filtrosExtras = [
    {
      campo: "tipo_animal_id",
      label: "Todos os tipos",
      opcoes: tipos.map((t) => ({ value: t.id, label: t.descricao })),
    },
  ];

  return (
    <CrudPage
      larga
      resource="animais"
      title={`Animais — ${propriedade.nome}`}
      fields={fields}
      columns={columns}
      campoBusca="nome"
      filtrosExtras={filtrosExtras}
    />
  );
}
