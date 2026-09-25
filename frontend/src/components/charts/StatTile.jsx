import { TrendingDown, TrendingUp } from "lucide-react";

function Sparkline({ valores }) {
  if (!valores || valores.length < 2) return null;
  const w = 64;
  const h = 24;
  const min = Math.min(...valores);
  const max = Math.max(...valores);
  const amplitude = max - min || 1;
  const pontos = valores.map((v, i) => {
    const x = (i / (valores.length - 1)) * w;
    const y = h - ((v - min) / amplitude) * h;
    return [x, y];
  });
  const linha = pontos.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
  const [ultimoX, ultimoY] = pontos[pontos.length - 1];

  return (
    <svg className="stat-tile-spark" width={w} height={h} viewBox={`0 0 ${w} ${h}`} aria-hidden="true">
      <polyline points={linha} fill="none" stroke="var(--color-text-faint)" strokeWidth="1.5" strokeLinejoin="round" strokeLinecap="round" />
      <circle cx={ultimoX} cy={ultimoY} r="2.5" fill="var(--color-primary)" />
    </svg>
  );
}

export default function StatTile({
  label,
  value,
  negativo = false,
  delta,
  deltaGoodWhenPositive = true,
  sparkline,
  deltaLabel = "vs. mês anterior",
}) {
  const temDelta = delta !== null && delta !== undefined && Number.isFinite(delta);
  const positivo = temDelta && delta >= 0;
  const bom = temDelta && positivo === deltaGoodWhenPositive;
  const Icone = positivo ? TrendingUp : TrendingDown;

  return (
    <div className="stat-tile">
      <span className="stat-tile-label">{label}</span>
      <div className="stat-tile-main">
        <span className={negativo ? "stat-tile-value negativo" : "stat-tile-value"}>{value}</span>
        {sparkline && <Sparkline valores={sparkline} />}
      </div>
      {temDelta && (
        <span className={bom ? "stat-tile-delta good" : "stat-tile-delta bad"}>
          <Icone size={13} />
          {positivo ? "+" : ""}
          {(delta * 100).toFixed(1)}%
          <span className="stat-tile-delta-label">{deltaLabel}</span>
        </span>
      )}
    </div>
  );
}
