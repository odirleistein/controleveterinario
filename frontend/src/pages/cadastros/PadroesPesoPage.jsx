import { useEffect, useState } from "react";
import api from "../../api/client";
import CrudPage from "../../components/CrudPage";

const fields = [
  {
    name: "raca_id", label: "Raça", type: "select", optionsResource: "racas",
    labelKey: "descricao", isId: true, required: true,
    optionsFilter: (r) => r.ativo,
  },
  { name: "idade_meses", label: "Idade (meses)", type: "number", step: "1", required: true },
  { name: "peso_ideal_kg", label: "Peso ideal (kg)", type: "number", required: true },
  { name: "observacao", label: "Observações", type: "textarea" },
];

const columns = [
  { key: "raca_descricao", label: "Raça" },
  { key: "idade_meses", label: "Idade (meses)", align: "right" },
  { key: "peso_ideal_kg", label: "Peso ideal (kg)", align: "right" },
  { key: "observacao", label: "Observações", opcional: true, render: (v) => v ?? "-" },
];

// Referencia comum (vale para qualquer propriedade): o peso que cada raca deve ter em
// cada idade. E contra ele que o peso real das pesagens e comparado.
export default function PadroesPesoPage() {
  const [racas, setRacas] = useState([]);

  useEffect(() => {
    api.get("/racas/").then((res) => setRacas(res.data));
  }, []);

  const filtrosExtras = [
    { campo: "raca_id", label: "Todas as raças", opcoes: racas.map((r) => ({ value: r.id, label: r.descricao })) },
  ];

  return (
    <CrudPage
      resource="padroes-peso"
      title="Peso ideal por raça e idade"
      fields={fields}
      columns={columns}
      filtrosExtras={filtrosExtras}
    />
  );
}
