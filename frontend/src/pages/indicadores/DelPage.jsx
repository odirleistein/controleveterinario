import { ArrowLeft } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../../api/client";
import BarrasComMeta from "../../components/charts/BarrasComMeta";
import StatTile from "../../components/charts/StatTile";
import MetasForm from "../../components/MetasForm";

const num = (v, casas = 0) =>
  v === null || v === undefined
    ? "-"
    : Number(v).toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });

/**
 * DEL (dias em lactacao) de cada vaca em lactacao, com a media do rebanho e a meta.
 * A meta e da propriedade: quem grava pode ajustar aqui.
 */
export default function DelPage() {
  const [dados, setDados] = useState(null);
  const [erro, setErro] = useState("");

  function carregar() {
    api
      .get("/indicadores/del")
      .then((res) => {
        setErro("");
        setDados(res.data);
      })
      .catch((err) => setErro(err.response?.data?.detail ?? "Erro ao carregar o indicador."));
  }

  useEffect(carregar, []);

  return (
    <div className="page page-larga">
      <div className="page-header">
        <h2>DEL — dias em lactação</h2>
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
            <StatTile label="DEL médio" value={num(dados.media, 1)} negativo={dados.media > dados.meta} />
            <StatTile label="Meta" value={num(dados.meta)} />
            <StatTile label="Vacas em lactação" value={`${dados.vacas_em_lactacao} de ${dados.total_vacas}`} />
            <StatTile label="Acima da meta" value={dados.acima_da_meta} negativo={dados.acima_da_meta > 0} />
          </div>

          <MetasForm campos={[{ chave: "DEL", rotulo: "Meta de DEL (dias)" }]} valores={{ DEL: dados.meta }} onSalvo={carregar} />

          <div className="chart-card">
            <div className="chart-card-header">
              <h3>DEL por vaca</h3>
            </div>
            {dados.linhas.length === 0 ? (
              <p className="empty-inline">
                Nenhuma vaca em lactação. O DEL conta a partir do último parto lançado em Reprodução.
              </p>
            ) : (
              <BarrasComMeta
                linhas={dados.linhas.map((l) => ({ id: l.animal_id, nome: l.animal_nome, valor: l.dias }))}
                meta={dados.meta}
                media={dados.media}
              />
            )}
          </div>
        </>
      )}
    </div>
  );
}
