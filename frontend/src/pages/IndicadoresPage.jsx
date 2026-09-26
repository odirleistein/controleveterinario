import { Link } from "react-router-dom";

// Os indicadores da planilha. A taxa de servico, a de concepcao, a de prenhez, o servico
// de concepcao e o IATF saem dos mesmos eventos e do mesmo periodo, por isso dividem um painel.
const INDICADORES = [
  { titulo: "DEL", detalhe: "Dias em lactação de cada vaca, contra a meta", to: "/indicadores/del" },
  {
    titulo: "Fertilidade",
    detalhe: "Taxa de serviço, concepção e prenhez, serviço de concepção e IATF",
    to: "/indicadores/fertilidade",
  },
  { titulo: "Intervalo entre partos", detalhe: "Dias entre um parto e o seguinte", to: "/indicadores/intervalo-partos" },
  { titulo: "Idade ao 1º parto", detalhe: "Do nascimento ao primeiro parto", to: "/indicadores/idade-primeiro-parto" },
  {
    titulo: "Idade de cobertura das novilhas",
    detalhe: "Do nascimento à primeira inseminação",
    to: "/indicadores/idade-cobertura",
  },
  { titulo: "Roda da reprodução", detalhe: "Quantas vacas em cada fase do ciclo", to: "/indicadores/roda" },
];

/** Porta de entrada dos paineis de indicadores da propriedade aberta. */
export default function IndicadoresPage() {
  return (
    <div className="page">
      <div className="page-header">
        <h2>Indicadores zootécnicos</h2>
      </div>
      <div className="indicadores-grid">
        {INDICADORES.map((i) => (
          <Link key={i.titulo} to={i.to} className="indicador-card">
            <strong>{i.titulo}</strong>
            <span>{i.detalhe}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
