import { useEffect, useState } from "react";
import api from "../api/client";
import { formatarData } from "../utils/format";

const kg = (v, casas = 1) =>
  v === null || v === undefined
    ? "-"
    : Number(v).toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });

/**
 * Cada pesagem da propriedade aberta contra o peso ideal da raca do animal na idade
 * que ele tinha no dia. Precisa da raca e da data de nascimento no cadastro do animal
 * e do peso ideal cadastrado para aquela raca naquela idade; senao mostra "-".
 */
export default function ComparativoPesoPage() {
  const [linhas, setLinhas] = useState(null);
  const [erro, setErro] = useState("");
  const [racas, setRacas] = useState([]);
  const [tipos, setTipos] = useState([]);
  const [racaId, setRacaId] = useState("");
  const [tipoId, setTipoId] = useState("");

  useEffect(() => {
    api.get("/racas/").then((res) => setRacas(res.data));
    api.get("/tipos-animal/").then((res) => setTipos(res.data));
  }, []);

  useEffect(() => {
    api
      .get("/pesagens/comparativo", { params: { raca_id: racaId || undefined, tipo_animal_id: tipoId || undefined } })
      .then((res) => {
        setErro("");
        setLinhas(res.data);
      })
      .catch((err) => setErro(err.response?.data?.detail ?? "Erro ao carregar o comparativo."));
  }, [racaId, tipoId]);

  return (
    <div className="page page-larga">
      <div className="page-header">
        <h2>Peso real x peso ideal</h2>
      </div>

      <div className="filtros">
        <select value={tipoId} onChange={(e) => setTipoId(e.target.value)}>
          <option value="">Todos os tipos</option>
          {tipos.map((t) => (
            <option key={t.id} value={t.id}>{t.descricao}</option>
          ))}
        </select>
        <select value={racaId} onChange={(e) => setRacaId(e.target.value)}>
          <option value="">Todas as raças</option>
          {racas.map((r) => (
            <option key={r.id} value={r.id}>{r.descricao}</option>
          ))}
        </select>
      </div>

      {erro && <div className="alert-error">{erro}</div>}
      {!linhas && !erro && <p>Carregando...</p>}
      {linhas && linhas.length === 0 && <p className="empty-inline">Nenhuma pesagem para comparar.</p>}

      {linhas && linhas.length > 0 && (
        <div className="table-wrap">
          <table className="data-table data-table-fluida">
            <thead>
              <tr>
                <th>Animal</th>
                <th className="col-opcional">Raça</th>
                <th>Data</th>
                <th className="valor">Idade (meses)</th>
                <th className="valor">Peso real (kg)</th>
                <th className="valor">Peso ideal (kg)</th>
                <th className="valor">Diferença (kg)</th>
                <th className="valor col-opcional">GMD real (kg/dia)</th>
                <th className="valor col-opcional">GMD ideal (kg/dia)</th>
              </tr>
            </thead>
            <tbody>
              {linhas.map((l) => (
                <tr key={l.pesagem_id}>
                  <td>{l.animal_nome}</td>
                  <td className="col-opcional">{l.raca_descricao ?? "-"}</td>
                  <td>{formatarData(l.data_pesagem)}</td>
                  <td className="valor">{l.idade_meses ?? "-"}</td>
                  <td className="valor">{kg(l.peso_real_kg)}</td>
                  <td className="valor">{kg(l.peso_ideal_kg)}</td>
                  <td className={l.diferenca_kg < 0 ? "valor negativo" : "valor"}>
                    {l.diferenca_kg > 0 ? "+" : ""}
                    {kg(l.diferenca_kg)}
                  </td>
                  <td className="valor col-opcional">{kg(l.gmd_real_kg, 3)}</td>
                  <td className="valor col-opcional">{kg(l.gmd_ideal_kg, 3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
