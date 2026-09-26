import { ArrowLeft } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api from "../api/client";
import StatTile from "../components/charts/StatTile";
import { formatarData, formatarMoeda } from "../utils/format";

const num = (v, casas = 2) =>
  v === null || v === undefined
    ? "-"
    : Number(v).toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });
const data = (v) => (v ? formatarData(v) : "-");

function Dado({ rotulo, valor }) {
  return (
    <div className="ficha-dado">
      <span className="ficha-dado-rotulo">{rotulo}</span>
      <span>{valor || "-"}</span>
    </div>
  );
}

/**
 * Ficha da vaca, como a aba da planilha: dados e genealogia, situacao e prazos
 * (calculados pela API a partir do historico), historico, partos, producao e pesagens.
 * So leitura: os lancamentos continuam nas telas de Reproducao, Producao e Pesagens.
 */
export default function FichaAnimalPage() {
  const { id } = useParams();
  const [ficha, setFicha] = useState(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api
      .get(`/animais/${id}/ficha`)
      .then((res) => setFicha(res.data))
      .catch((err) => setErro(err.response?.data?.detail ?? "Erro ao carregar a ficha."));
  }, [id]);

  return (
    <div className="page page-larga">
      <div className="page-header">
        <h2>{ficha ? `Ficha — ${ficha.animal.nome}` : "Ficha do animal"}</h2>
        <Link to="/animais" className="btn-secondary btn-com-icone">
          <ArrowLeft size={16} />
          Animais
        </Link>
      </div>

      {erro && <div className="alert-error">{erro}</div>}
      {!ficha && !erro && <p>Carregando...</p>}

      {ficha && (
        <>
          <div className="kpi-row">
            <StatTile label="Situação" value={ficha.situacao} />
            <StatTile label="Dias em lactação (DEL)" value={ficha.dias_em_lactacao ?? "-"} />
            <StatTile label="Doses até a confirmação" value={ficha.doses_ate_confirmacao} />
            <StatTile label="Litros da lactação atual" value={num(ficha.litros_lactacao_atual)} />
          </div>

          <div className="ficha-blocos">
            <div className="chart-card">
              <div className="chart-card-header">
                <h3>Dados</h3>
              </div>
              <Dado rotulo="Nome" valor={ficha.animal.nome} />
              <Dado rotulo="Nº / brinco" valor={ficha.animal.codigo} />
              <Dado rotulo="Tipo" valor={ficha.animal.tipo_descricao} />
              <Dado rotulo="Raça" valor={ficha.animal.raca_descricao} />
              <Dado rotulo="Nascimento" valor={data(ficha.animal.data_nascimento)} />
              <Dado rotulo="Peso ao nascimento" valor={ficha.animal.peso_nascimento_kg ? `${num(ficha.animal.peso_nascimento_kg)} kg` : null} />
              <Dado rotulo="Observações" valor={ficha.animal.observacao} />
            </div>

            <div className="chart-card">
              <div className="chart-card-header">
                <h3>Genealogia</h3>
              </div>
              <Dado rotulo="Mãe" valor={ficha.genealogia.mae} />
              <Dado rotulo="Avô materno" valor={ficha.genealogia.avo_materno} />
              <Dado rotulo="Bisavô materno" valor={ficha.genealogia.bisavo_materno} />
              <Dado rotulo="Pai" valor={ficha.genealogia.pai} />
              <Dado rotulo="Avô paterno" valor={ficha.genealogia.avo_paterno} />
              <Dado rotulo="Bisavô paterno" valor={ficha.genealogia.bisavo_paterno} />
            </div>

            <div className="chart-card">
              <div className="chart-card-header">
                <h3>Prazos</h3>
              </div>
              <Dado rotulo="Inseminação" valor={data(ficha.prazos.inseminacao)} />
              <Dado rotulo="Retorno de cio" valor={data(ficha.prazos.retorno_cio)} />
              <Dado rotulo="Secagem" valor={data(ficha.prazos.secagem)} />
              <Dado rotulo="Provável parto" valor={data(ficha.prazos.provavel_parto)} />
              <p className="ficha-nota">Calculados pela última inseminação (21 dias para o cio, 282 de gestação, seca 60 dias antes).</p>
            </div>

            <div className="chart-card">
              <div className="chart-card-header">
                <h3>Partos</h3>
              </div>
              {ficha.partos.length === 0 && <p className="empty-inline">Nenhum parto lançado.</p>}
              {ficha.partos.map((p) => (
                <Dado
                  key={p.numero}
                  rotulo={`Parto ${p.numero}`}
                  valor={`${data(p.data_evento)}${p.sexo_cria ? ` — ${p.sexo_cria === "F" ? "fêmea" : "macho"}` : ""}`}
                />
              ))}
            </div>
          </div>

          <div className="chart-card">
            <div className="chart-card-header">
              <h3>Histórico</h3>
              <Link to="/reproducao" className="btn-secondary">Lançar evento</Link>
            </div>
            {ficha.historico.length === 0 ? (
              <p className="empty-inline">Nenhum evento lançado.</p>
            ) : (
              <div className="table-wrap">
                <table className="data-table data-table-fluida">
                  <thead>
                    <tr>
                      <th>Data</th>
                      <th>Evento</th>
                      <th>Touro</th>
                      <th className="valor">Sêmen R$</th>
                      <th className="col-opcional">Observações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ficha.historico.map((e) => (
                      <tr key={e.id}>
                        <td>{data(e.data_evento)}</td>
                        <td>{e.tipo_evento_descricao}</td>
                        <td>{e.reprodutor_nome ?? "-"}</td>
                        <td className="valor">{e.valor_semen == null ? "-" : formatarMoeda(e.valor_semen)}</td>
                        <td className="col-opcional">{e.observacao ?? "-"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <div className="chart-card">
            <div className="chart-card-header">
              <h3>Produção de leite</h3>
              <Link to="/producao-leite" className="btn-secondary">Lançar produção</Link>
            </div>
            {ficha.media_litros_dia_lactacao_atual != null && (
              <p className="ficha-nota">Média da lactação atual: {num(ficha.media_litros_dia_lactacao_atual)} litros/dia.</p>
            )}
            {ficha.producao.length === 0 ? (
              <p className="empty-inline">Nenhuma produção lançada.</p>
            ) : (
              <div className="table-wrap">
                <table className="data-table data-table-fluida">
                  <thead>
                    <tr>
                      <th>Data</th>
                      <th className="valor">Litros</th>
                      <th className="valor">Dias</th>
                      <th className="valor">Litros/dia</th>
                      <th className="valor">Acumulado da lactação</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ficha.producao.map((p) => (
                      <tr key={p.id}>
                        <td>{data(p.data_producao)}</td>
                        <td className="valor">{num(p.litros)}</td>
                        <td className="valor">{p.dias_referentes}</td>
                        <td className="valor">{num(p.litros_por_dia)}</td>
                        <td className="valor">{num(p.acumulado_lactacao)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {ficha.pesagens.length > 0 && (
            <div className="chart-card">
              <div className="chart-card-header">
                <h3>Pesagens</h3>
                <Link to="/pesagens" className="btn-secondary">Lançar pesagem</Link>
              </div>
              <div className="table-wrap">
                <table className="data-table data-table-fluida">
                  <thead>
                    <tr>
                      <th>Data</th>
                      <th className="valor">Peso (kg)</th>
                      <th className="col-opcional">Observações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ficha.pesagens.map((p) => (
                      <tr key={p.id}>
                        <td>{data(p.data_pesagem)}</td>
                        <td className="valor">{num(p.peso_kg)}</td>
                        <td className="col-opcional">{p.observacao ?? "-"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
