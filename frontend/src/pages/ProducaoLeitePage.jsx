import { useEffect, useMemo, useState } from "react";
import api from "../api/client";
import CrudPage from "../components/CrudPage";
import { useAuth } from "../context/AuthContext";
import { camposAnimalComTipo } from "../utils/camposAnimal";
import { formatarData, hoje } from "../utils/format";

const kg = (v) => Number(v).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

const camposBase = [
  { name: "data_producao", label: "Data (no lançamento mensal, o dia do fechamento)", type: "date", required: true, default: hoje() },
  { name: "litros", label: "Litros", type: "number", required: true },
  {
    name: "dias_referentes", label: "Dias que o lançamento cobre (1 = diário; 30 = total do mês)",
    type: "number", step: "1", required: true, default: 1,
  },
  { name: "observacao", label: "Observações", type: "textarea" },
];

const columns = [
  { key: "animal_nome", label: "Animal" },
  { key: "data_producao", label: "Data", render: (v) => formatarData(v) },
  { key: "litros", label: "Litros", align: "right", render: (v) => kg(v) },
  { key: "dias_referentes", label: "Dias", align: "right" },
  { key: "litros_por_dia", label: "Litros/dia", align: "right", render: (v) => kg(v) },
  { key: "observacao", label: "Observações", opcional: true, render: (v) => v ?? "-" },
];

// Um lancamento por animal e data: diario, ou o total do mes numa data so (dias > 1).
export default function ProducaoLeitePage() {
  const { propriedade } = useAuth();
  const [tipos, setTipos] = useState([]);

  useEffect(() => {
    api.get("/tipos-animal/").then((res) => setTipos(res.data));
  }, []);

  // So os tipos que produzem leite: nao ha producao de terneiras nem de novilhas.
  const produtores = tipos.filter((t) => t.ativo && t.produz_leite);

  // Com um unico tipo produtor (so "Vacas"), o formulario ja abre com ele escolhido.
  const fields = useMemo(() => {
    const unico = produtores.length === 1 ? produtores[0].id : undefined;
    const [tipo, animal] = camposAnimalComTipo({ soProdutoresDeLeite: true });
    return [{ ...tipo, default: unico }, animal, ...camposBase];
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tipos]);

  const filtrosExtras = [
    {
      campo: "tipo_animal_id",
      label: "Todos os tipos",
      opcoes: produtores.map((t) => ({ value: t.id, label: t.descricao })),
    },
  ];

  return (
    <CrudPage
      larga
      resource="producoes-leite"
      title={`Produção de leite — ${propriedade.nome}`}
      fields={fields}
      columns={columns}
      campoBusca="animal_nome"
      filtrosExtras={filtrosExtras}
    />
  );
}
