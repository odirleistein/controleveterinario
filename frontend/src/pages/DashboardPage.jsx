import { useEffect, useState } from "react";
import api from "../api/client";
import StatTile from "../components/charts/StatTile";
import { useAuth } from "../context/AuthContext";

/** Barras horizontais simples: o maior valor ocupa a trilha inteira. */
function BarrasRanking({ linhas, rotulo }) {
  if (linhas.length === 0) return <p className="empty-inline">Nada cadastrado ainda.</p>;
  const maior = Math.max(...linhas.map((l) => l.total), 1);
  return (
    <div className="bar-rows">
      {linhas.map((l) => (
        <div className="bar-row" key={l[rotulo]}>
          <span className="bar-row-label">
            <span className="bar-row-nome">{l[rotulo]}</span>
          </span>
          <span className="bar-track">
            <span
              className="bar-fill"
              style={{ width: `${Math.max((l.total / maior) * 100, 3)}%`, background: "var(--color-primary)" }}
            />
          </span>
          <span className="bar-row-value">{l.total}</span>
        </div>
      ))}
    </div>
  );
}

export default function DashboardPage() {
  const { usuario } = useAuth();
  const [resumo, setResumo] = useState(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api
      .get("/dashboard/resumo")
      .then((res) => setResumo(res.data))
      .catch(() => setErro("Erro ao carregar o painel."));
  }, []);

  return (
    <div className="page">
      <div className="page-header">
        <h2>Visão Geral</h2>
      </div>
      <p className="subtitle">
        Olá, {usuario?.nome}. {usuario?.papel_nome !== "MASTER" && "Os números abaixo consideram só as propriedades a que você tem acesso."}
      </p>

      {erro && <div className="alert-error">{erro}</div>}
      {!resumo && !erro && <p>Carregando...</p>}

      {resumo && (
        <>
          <div className="kpi-row">
            <StatTile label="Propriedades ativas" value={resumo.propriedades} />
            <StatTile label="Animais" value={resumo.animais} />
            <StatTile label="Veterinários" value={resumo.veterinarios} />
            <StatTile label="Pessoas" value={resumo.pessoas} />
          </div>

          <div className="graficos-duplo">
            <div className="chart-card">
              <div className="chart-card-header">
                <h3>Animais por tipo</h3>
              </div>
              <BarrasRanking linhas={resumo.animais_por_tipo} rotulo="tipo" />
            </div>
            <div className="chart-card">
              <div className="chart-card-header">
                <h3>Propriedades por cidade</h3>
              </div>
              <BarrasRanking linhas={resumo.propriedades_por_cidade} rotulo="cidade" />
            </div>
          </div>
        </>
      )}
    </div>
  );
}
