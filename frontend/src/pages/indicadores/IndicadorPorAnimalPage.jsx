import { ArrowLeft } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../../api/client";
import BarrasComMeta from "../../components/charts/BarrasComMeta";
import StatTile from "../../components/charts/StatTile";
import MetasForm from "../../components/MetasForm";
import SeletorPeriodo from "../../components/SeletorPeriodo";
import { periodoInicial } from "../../utils/periodo";

const num = (v, casas = 1) =>
  v === null || v === undefined
    ? "-"
    : Number(v).toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });

/**
 * Painel de um indicador medido animal a animal (intervalo entre partos, idade ao
 * primeiro parto, idade de cobertura): media contra a meta, e uma barra por animal.
 * Cada painel so diz qual endpoint consultar, qual meta usar e como se explica.
 */
function IndicadorPorAnimalPage({ titulo, endpoint, metaChave, unidade, rotuloMeta, casas, explicacao, vazio }) {
  const [periodo, setPeriodo] = useState(periodoInicial);
  const [dados, setDados] = useState(null);
  const [erro, setErro] = useState("");

  function carregar() {
    if (!periodo.inicio || !periodo.fim) return;
    api
      .get(endpoint, { params: { data_inicio: periodo.inicio, data_fim: periodo.fim } })
      .then((res) => {
        setErro("");
        setDados(res.data);
      })
      .catch((err) => setErro(err.response?.data?.detail ?? "Erro ao carregar o indicador."));
  }

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(carregar, [periodo.inicio, periodo.fim, endpoint]);

  return (
    <div className="page page-larga">
      <div className="page-header">
        <h2>{titulo}</h2>
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
            <StatTile label={`Média (${unidade})`} value={num(dados.media, casas)} negativo={dados.media > dados.meta} />
            <StatTile label={`Meta (${unidade})`} value={num(dados.meta, casas)} />
            <StatTile label="Animais no cálculo" value={dados.total} />
            <StatTile label="Acima da meta" value={dados.acima_da_meta} negativo={dados.acima_da_meta > 0} />
          </div>

          <MetasForm
            campos={[{ chave: metaChave, rotulo: rotuloMeta }]}
            valores={{ [metaChave]: dados.meta }}
            onSalvo={carregar}
          />

          <div className="chart-card">
            <div className="chart-card-header">
              <h3>{titulo} por animal</h3>
            </div>
            <p className="ficha-nota">{explicacao}</p>
            {dados.linhas.length === 0 ? (
              <p className="empty-inline">{vazio}</p>
            ) : (
              <BarrasComMeta
                linhas={dados.linhas.map((l) => ({ id: l.animal_id, nome: l.animal_nome, valor: l.valor }))}
                meta={dados.meta}
                media={dados.media}
                casas={casas}
              />
            )}
          </div>
        </>
      )}
    </div>
  );
}

export function IntervaloPartosPage() {
  return (
    <IndicadorPorAnimalPage
      titulo="Intervalo entre partos"
      endpoint="/indicadores/intervalo-partos"
      metaChave="INTERVALO_PARTOS"
      unidade="dias"
      rotuloMeta="Meta (dias)"
      casas={0}
      explicacao="Dias entre um parto e o seguinte, dos partos ocorridos no período. Cada barra é a média da vaca; a média geral considera todos os intervalos."
      vazio="Nenhuma vaca com dois partos seguidos lançados no período."
    />
  );
}

export function IdadePrimeiroPartoPage() {
  return (
    <IndicadorPorAnimalPage
      titulo="Idade ao 1º parto"
      endpoint="/indicadores/idade-primeiro-parto"
      metaChave="IDADE_PRIMEIRO_PARTO"
      unidade="meses"
      rotuloMeta="Meta (meses)"
      casas={1}
      explicacao="Meses do nascimento ao primeiro parto lançado, dos partos ocorridos no período. Precisa da data de nascimento no cadastro do animal."
      vazio="Nenhuma vaca com data de nascimento e primeiro parto lançado no período."
    />
  );
}

export function IdadeCoberturaPage() {
  return (
    <IndicadorPorAnimalPage
      titulo="Idade de cobertura das novilhas"
      endpoint="/indicadores/idade-cobertura"
      metaChave="IDADE_COBERTURA"
      unidade="meses"
      rotuloMeta="Meta (meses)"
      casas={1}
      explicacao="Meses do nascimento à primeira inseminação lançada, das inseminações feitas no período. Precisa da data de nascimento no cadastro do animal."
      vazio="Nenhum animal com data de nascimento e primeira inseminação lançada no período."
    />
  );
}
