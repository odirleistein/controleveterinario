import { Scale } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";
import StatTile from "../components/charts/StatTile";
import { useAuth } from "../context/AuthContext";

/** Barras horizontais simples: o maior valor ocupa a trilha inteira. */
function BarrasRanking({ linhas, rotulo }) {
  if (linhas.length === 0) return <p className="empty-inline">Nenhum animal cadastrado ainda.</p>;
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

/** Visao geral de UMA propriedade: a que esta aberta (cabecalho X-Propriedade-Id). */
export default function DashboardPage() {
  const { propriedades } = useAuth();
  const [resumo, setResumo] = useState(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api
      .get("/dashboard/resumo")
      .then((res) => setResumo(res.data))
      .catch((err) => setErro(err.response?.data?.detail ?? "Erro ao carregar o painel."));
  }, []);

  return (
    <div className="page">
      <div className="page-header">
        <h2>{resumo ? resumo.propriedade_nome : "Visão Geral"}</h2>
        {propriedades.length > 1 && (
          <Link to="/comparativo" className="btn-secondary btn-com-icone">
            <Scale size={16} />
            Comparar com outras
          </Link>
        )}
      </div>
      {resumo && (
        <p className="subtitle">
          {resumo.proprietario_nome} · {resumo.cidade_uf}
        </p>
      )}

      {erro && <div className="alert-error">{erro}</div>}
      {!resumo && !erro && <p>Carregando...</p>}

      {resumo && (
        <>
          <div className="kpi-row">
            <StatTile label="Animais" value={resumo.animais} />
            <StatTile label="Veterinários que atendem" value={resumo.veterinarios} />
            <StatTile label="Usuários com acesso" value={resumo.usuarios} />
          </div>

          <div className="chart-card">
            <div className="chart-card-header">
              <h3>Animais por tipo</h3>
            </div>
            <BarrasRanking linhas={resumo.animais_por_tipo} rotulo="tipo" />
          </div>
        </>
      )}
    </div>
  );
}
