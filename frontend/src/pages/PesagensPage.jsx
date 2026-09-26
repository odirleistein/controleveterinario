import { useEffect, useState } from "react";
import api from "../api/client";
import CrudPage from "../components/CrudPage";
import { useAuth } from "../context/AuthContext";
import { camposAnimalComTipo } from "../utils/camposAnimal";
import { formatarData, hoje } from "../utils/format";

const fields = [
  ...camposAnimalComTipo(),
  { name: "data_pesagem", label: "Data da pesagem", type: "date", required: true, default: hoje() },
  { name: "peso_kg", label: "Peso real (kg)", type: "number", required: true },
  { name: "observacao", label: "Observações", type: "textarea" },
];

const columns = [
  { key: "animal_nome", label: "Animal" },
  { key: "data_pesagem", label: "Data", render: (v) => formatarData(v) },
  { key: "peso_kg", label: "Peso real (kg)", align: "right" },
  { key: "observacao", label: "Observações", opcional: true, render: (v) => v ?? "-" },
];

// Peso real lancado na propriedade aberta. O animal escolhido tem de ser dela (a API confere).
export default function PesagensPage() {
  const { propriedade } = useAuth();
  const [tipos, setTipos] = useState([]);

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
      resource="pesagens"
      title={`Pesagens — ${propriedade.nome}`}
      fields={fields}
      columns={columns}
      campoBusca="animal_nome"
      filtrosExtras={filtrosExtras}
    />
  );
}
