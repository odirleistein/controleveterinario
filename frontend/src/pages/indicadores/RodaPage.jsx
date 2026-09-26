import { ArrowLeft } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../../api/client";
import StatTile from "../../components/charts/StatTile";

// Uma cor por fase, na ordem em que a API devolve.
const CORES = {
  Vazia: "#94a3b8",
  Inseminada: "#f59e0b",
  Prenhe: "#15915a",
  Seca: "#4f46e5",
  Descartada: "#e11d48",
};

/** Roda da reproducao: quantas vacas estao hoje em cada fase do ciclo (rosca + legenda). */
export default function RodaPage() {
  const [dados, setDados] = useState(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api
      .get("/indicadores/roda")
      .then((res) => setDados(res.data))
      .catch((err) => setErro(err.response?.data?.detail ?? "Erro ao carregar o indicador."));
  }, []);

  // conic-gradient com uma fatia por fase, uma apos a outra.
  function gradiente(fases, total) {
    let acumulado = 0;
    const partes = fases
      .filter((f) => f.quantidade > 0)
      .map((f) => {
        const de = (acumulado / total) * 100;
        acumulado += f.quantidade;
        return `${CORES[f.situacao]} ${de}% ${(acumulado / total) * 100}%`;
      });
    return `conic-gradient(${partes.join(", ")})`;
  }

  return (
    <div className="page page-larga">
      <div className="page-header">
        <h2>Roda da reprodução</h2>
        <Link to="/indicadores" className="btn-secondary btn-com-icone">
          <ArrowLeft size={16} />
          Indicadores
        </Link>
      </div>

      {erro && <div className="alert-error">{erro}</div>}
      {!dados && !erro && <p>Carregando...</p>}

      {dados && (
        <>
          <div className="kpi-row">
            <StatTile label="Vacas" value={dados.total_vacas} />
            <StatTile label="Em lactação" value={dados.em_lactacao} />
            {dados.fases
              .filter((f) => ["Prenhe", "Inseminada"].includes(f.situacao))
              .map((f) => (
                <StatTile key={f.situacao} label={f.situacao === "Prenhe" ? "Prenhes" : "Inseminadas"} value={f.quantidade} />
              ))}
          </div>

          <div className="chart-card">
            <div className="chart-card-header">
              <h3>Situação atual das vacas</h3>
            </div>
            {dados.total_vacas === 0 ? (
              <p className="empty-inline">Nenhuma vaca ativa. Só entram animais de tipos que produzem leite.</p>
            ) : (
              <div className="roda-conteudo">
                <div className="roda-rosca" style={{ background: gradiente(dados.fases, dados.total_vacas) }} role="img" aria-label="Vacas por situação">
                  <span>{dados.total_vacas}</span>
                </div>
                <ul className="roda-legenda">
                  {dados.fases.map((f) => (
                    <li key={f.situacao}>
                      <i style={{ background: CORES[f.situacao] }} />
                      <span>{f.situacao}</span>
                      <strong>{f.quantidade}</strong>
                      <em>{Math.round((f.quantidade / dados.total_vacas) * 100)}%</em>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <p className="ficha-nota">
              A situação vem do último evento lançado de cada vaca. "Vazia" inclui as que acabaram de parir e as que voltaram ao cio.
            </p>
          </div>
        </>
      )}
    </div>
  );
}
