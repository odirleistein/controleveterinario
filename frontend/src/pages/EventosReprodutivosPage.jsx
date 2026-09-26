import { useEffect, useMemo, useState } from "react";
import api from "../api/client";
import CrudPage from "../components/CrudPage";
import { useAuth } from "../context/AuthContext";
import { camposAnimalComTipo } from "../utils/camposAnimal";
import { formatarData, formatarMoeda, hoje } from "../utils/format";

const SEXOS = [
  { value: "F", label: "Fêmea" },
  { value: "M", label: "Macho" },
];

const columns = [
  { key: "animal_nome", label: "Animal" },
  { key: "data_evento", label: "Data", render: (v) => formatarData(v) },
  { key: "tipo_evento_descricao", label: "Evento" },
  { key: "reprodutor_nome", label: "Touro", render: (v) => v ?? "-" },
  { key: "valor_semen", label: "Sêmen R$", align: "right", opcional: true, render: (v) => (v == null ? "-" : formatarMoeda(v)) },
  { key: "observacao", label: "Observações", opcional: true, render: (v) => v ?? "-" },
];

// Historico reprodutivo da vaca na propriedade aberta. Os campos do touro/sêmen so aparecem
// na inseminacao/IATF e os da cria so no parto: a tela usa o `codigo` do tipo de evento.
export default function EventosReprodutivosPage() {
  const { propriedade } = useAuth();
  const [tipos, setTipos] = useState([]);
  const [tiposAnimal, setTiposAnimal] = useState([]);

  useEffect(() => {
    api.get("/tipos-evento/").then((res) => setTipos(res.data));
    api.get("/tipos-animal/").then((res) => setTiposAnimal(res.data));
  }, []);

  const fields = useMemo(() => {
    const codigoDe = (dados) => tipos.find((t) => String(t.id) === String(dados?.tipo_evento_id))?.codigo;
    const ehInseminacao = (dados) => ["INSEMINACAO", "IATF"].includes(codigoDe(dados));
    const ehParto = (dados) => codigoDe(dados) === "PARTO";
    return [
      ...camposAnimalComTipo(),
      {
        name: "tipo_evento_id", label: "Evento", type: "select", optionsResource: "tipos-evento",
        labelKey: "descricao", isId: true, required: true, optionsFilter: (t) => t.ativo,
      },
      { name: "data_evento", label: "Data", type: "date", required: true, default: hoje() },
      {
        name: "reprodutor_id", label: "Touro", type: "select", optionsResource: "reprodutores",
        labelKey: "nome", isId: true, mostrarSe: ehInseminacao,
        optionsFilter: (r) => r.ativo && r.sexo === "M",
      },
      { name: "valor_semen", label: "Sêmen R$", type: "number", mostrarSe: ehInseminacao },
      { name: "sexo_cria", label: "Sexo da cria", type: "select", options: SEXOS, mostrarSe: ehParto },
      {
        name: "cria_animal_id", label: "Cria (se já cadastrada)", type: "select", optionsResource: "animais",
        labelKey: "nome", isId: true, mostrarSe: ehParto, optionsFilter: (a) => a.ativo,
      },
      { name: "observacao", label: "Observações", type: "textarea" },
    ];
  }, [tipos]);

  const filtrosExtras = [
    { campo: "tipo_evento_id", label: "Todos os eventos", opcoes: tipos.map((t) => ({ value: t.id, label: t.descricao })) },
    { campo: "tipo_animal_id", label: "Todos os tipos", opcoes: tiposAnimal.map((t) => ({ value: t.id, label: t.descricao })) },
  ];

  return (
    <CrudPage
      larga
      resource="eventos-reprodutivos"
      title={`Reprodução — ${propriedade.nome}`}
      fields={fields}
      columns={columns}
      campoBusca="animal_nome"
      filtrosExtras={filtrosExtras}
    />
  );
}
