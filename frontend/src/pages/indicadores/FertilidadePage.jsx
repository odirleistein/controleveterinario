import { ArrowLeft } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../../api/client";
import StatTile from "../../components/charts/StatTile";
import MetasForm from "../../components/MetasForm";
import SeletorPeriodo from "../../components/SeletorPeriodo";
import { periodoInicial } from "../../utils/periodo";
import { formatarData } from "../../utils/format";

const num = (v, casas = 1) =>
  v === null || v === undefined
    ? "-"
    : Number(v).toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });
const pct = (v) => (v === null || v === undefined ? "-" : `${num(v)}%`);

const CAMPOS_METAS = [
  { chave: "TAXA_SERVICO", rotulo: "Meta taxa de serviço (%)" },
  { chave: "TAXA_CONCEPCAO", rotulo: "Meta taxa de concepção (%)" },
  { chave: "TAXA_PRENHEZ", rotulo: "Meta taxa de prenhez (%)" },
  { chave: "SERVICO_CONCEPCAO", rotulo: "Meta serviço de concepção (doses)", passo: "0.1" },
  { chave: "PERIODO_ESPERA", rotulo: "Período de espera pós-parto (dias)" },
];

function LinhaGrupo({ rotulo, grupo }) {
  return (
    <tr>
      <td>{rotulo}</td>
      <td className="valor">{grupo.inseminacoes}</td>
      <td className="valor">{grupo.concepcoes}</td>
      <td className="valor">{grupo.nao_concebeu}</td>
      <td className="valor">{grupo.pendentes}</td>
      <td className="valor">{pct(grupo.taxa_concepcao)}</td>
    </tr>
  );
}

/**
 * Taxas reprodutivas do periodo: taxa de servico, de concepcao, de prenhez, servico de
 * concepcao (doses por prenhez) e IATF x inseminacao convencional. Reune cinco
 * indicadores da planilha porque saem dos mesmos eventos e do mesmo periodo.
 */
export default function FertilidadePage() {
  const [periodo, setPeriodo] = useState(periodoInicial);
  const [dados, setDados] = useState(null);
  const [erro, setErro] = useState("");

  function carregar() {
    if (!periodo.inicio || !periodo.fim) return;
    api
      .get("/indicadores/fertilidade", { params: { data_inicio: periodo.inicio, data_fim: periodo.fim } })
      .then((res) => {
        setErro("");
        setDados(res.data);
      })
      .catch((err) => setErro(err.response?.data?.detail ?? "Erro ao carregar o indicador."));
  }

  useEffect(carregar, [periodo.inicio, periodo.fim]);

  const m = dados?.metas;
  // Taxas: abaixo da meta e ruim. Serviço de concepção: acima da meta e ruim.
  const abaixo = (v, meta) => v !== null && v < meta;

  return (
    <div className="page page-larga">
      <div className="page-header">
        <h2>Fertilidade — serviço, concepção e prenhez</h2>
        <Link to="/indicadores" className="btn-secondary btn-com-icone">
          <ArrowLeft size={16} />
          Indicadores
        </Link>
      </div>

      <SeletorPeriodo valor={periodo} onChange={setPeriodo} />

      {erro && <div className="alert-error">{erro}</div>}
      {!dados && !erro && <p>Carregando...</p>}

      {dados && (
        <>
          <div className="kpi-row">
            <StatTile label={`Taxa de serviço · meta ${num(m.TAXA_SERVICO, 0)}%`} value={pct(dados.taxa_servico)} negativo={abaixo(dados.taxa_servico, m.TAXA_SERVICO)} />
            <StatTile label={`Taxa de concepção · meta ${num(m.TAXA_CONCEPCAO, 0)}%`} value={pct(dados.taxa_concepcao)} negativo={abaixo(dados.taxa_concepcao, m.TAXA_CONCEPCAO)} />
            <StatTile label={`Taxa de prenhez · meta ${num(m.TAXA_PRENHEZ, 0)}%`} value={pct(dados.taxa_prenhez)} negativo={abaixo(dados.taxa_prenhez, m.TAXA_PRENHEZ)} />
            <StatTile
              label={`Serviço de concepção · meta ${num(m.SERVICO_CONCEPCAO)}`}
              value={num(dados.servico_concepcao, 2)}
              negativo={dados.servico_concepcao !== null && dados.servico_concepcao > m.SERVICO_CONCEPCAO}
            />
          </div>

          <MetasForm campos={CAMPOS_METAS} valores={m} onSalvo={carregar} />

          <div className="chart-card">
            <div className="chart-card-header">
              <h3>IATF x inseminação convencional</h3>
              <span className="ficha-nota">IATF: {pct(dados.percentual_iatf)} das inseminações</span>
            </div>
            <div className="table-wrap">
              <table className="data-table data-table-fluida">
                <thead>
                  <tr>
                    <th />
                    <th className="valor">Inseminações</th>
                    <th className="valor">Prenhezes</th>
                    <th className="valor">Não pegou</th>
                    <th className="valor">Sem resultado</th>
                    <th className="valor">Taxa de concepção</th>
                  </tr>
                </thead>
                <tbody>
                  <LinhaGrupo rotulo="Geral" grupo={dados.geral} />
                  <LinhaGrupo rotulo="IATF" grupo={dados.iatf} />
                  <LinhaGrupo rotulo="Convencional" grupo={dados.convencional} />
                </tbody>
              </table>
            </div>
            <p className="ficha-nota">
              "Sem resultado" são inseminações ainda sem prenhez confirmada nem retorno de cio: ficam fora da taxa de concepção.
            </p>
          </div>

          <div className="chart-card">
            <div className="chart-card-header">
              <h3>Taxa de serviço por ciclo de 21 dias</h3>
            </div>
            {dados.ciclos.length === 0 ? (
              <p className="empty-inline">O período precisa ter pelo menos 21 dias para formar um ciclo.</p>
            ) : (
              <div className="table-wrap">
                <table className="data-table data-table-fluida">
                  <thead>
                    <tr>
                      <th>Ciclo (início)</th>
                      <th className="valor">Vacas aptas</th>
                      <th className="valor">Inseminadas</th>
                      <th className="valor">Taxa de serviço</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dados.ciclos.map((c) => (
                      <tr key={c.inicio}>
                        <td>{formatarData(c.inicio)}</td>
                        <td className="valor">{c.elegiveis}</td>
                        <td className="valor">{c.servidas}</td>
                        <td className={abaixo(c.taxa_servico, m.TAXA_SERVICO) ? "valor negativo" : "valor"}>{pct(c.taxa_servico)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <p className="ficha-nota">
              Vaca apta: vazia (sem inseminação em andamento, prenhez ou secagem) e com mais de {num(m.PERIODO_ESPERA, 0)} dias
              desde o parto. Só entram vacas que já têm algum evento lançado. A taxa de prenhez é a taxa de serviço multiplicada pela
              taxa de concepção; o serviço de concepção é o número de inseminações por prenhez.
            </p>
          </div>
        </>
      )}
    </div>
  );
}
