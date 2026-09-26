import { calcularPeriodo } from "../utils/periodo";

const OPCOES = [
  { chave: "90d", rotulo: "Últimos 90 dias" },
  { chave: "6m", rotulo: "Últimos 6 meses" },
  { chave: "12m", rotulo: "Últimos 12 meses" },
  { chave: "ano", rotulo: "Este ano" },
  { chave: "ano-passado", rotulo: "Ano passado" },
  { chave: "custom", rotulo: "Personalizado" },
];

/**
 * Escolha do periodo de um indicador: atalhos (ultimos meses, ano) ou datas livres.
 * valor = { chave, inicio, fim }; a tela deve so consultar quando inicio e fim existem.
 */
export default function SeletorPeriodo({ valor, onChange }) {
  function escolher(chave) {
    onChange(chave === "custom" ? { ...valor, chave } : { chave, ...calcularPeriodo(chave) });
  }

  return (
    <div className="filtros">
      <select value={valor.chave} onChange={(e) => escolher(e.target.value)} aria-label="Período">
        {OPCOES.map((o) => (
          <option key={o.chave} value={o.chave}>
            {o.rotulo}
          </option>
        ))}
      </select>
      {valor.chave === "custom" ? (
        <>
          <label className="filtro-data">
            De
            <input type="date" value={valor.inicio} onChange={(e) => onChange({ ...valor, inicio: e.target.value })} />
          </label>
          <label className="filtro-data">
            até
            <input type="date" value={valor.fim} onChange={(e) => onChange({ ...valor, fim: e.target.value })} />
          </label>
        </>
      ) : (
        <span className="ficha-nota">
          {valor.inicio.split("-").reverse().join("/")} a {valor.fim.split("-").reverse().join("/")}
        </span>
      )}
    </div>
  );
}
