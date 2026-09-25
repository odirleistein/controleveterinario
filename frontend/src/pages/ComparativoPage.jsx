import { useEffect, useState } from "react";
import api from "../api/client";
import MultiSelect from "../components/MultiSelect";

/**
 * Propriedades lado a lado, para o veterinario analisar as que atende ou para o
 * produtor que tem mais de uma. So entram as propriedades a que o usuario tem
 * acesso (a API recorta); sem escolher nenhuma no filtro, compara todas elas.
 */
export default function ComparativoPage() {
  const [opcoes, setOpcoes] = useState([]);
  const [escolhidas, setEscolhidas] = useState([]);
  const [dados, setDados] = useState(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api
      .get("/propriedades/")
      .then((res) => setOpcoes(res.data.filter((p) => p.ativa).map((p) => ({ value: p.id, label: p.nome }))))
      .catch(() => setOpcoes([]));
  }, []);

  useEffect(() => {
    api
      .get("/dashboard/comparativo", { params: { propriedade_id: escolhidas.map(Number) } })
      .then((res) => {
        setErro("");
        setDados(res.data);
      })
      .catch((err) => setErro(err.response?.data?.detail ?? "Erro ao carregar o comparativo."));
  }, [escolhidas]);

  const maiorRebanho = Math.max(...(dados?.linhas ?? []).map((l) => l.animais), 1);

  return (
    <div className="page page-larga">
      <div className="page-header">
        <h2>Comparativo entre propriedades</h2>
      </div>

      <div className="filtros">
        <MultiSelect
          value={escolhidas}
          onChange={setEscolhidas}
          options={opcoes}
          todasLabel="Todas as minhas propriedades"
          nomeMultiplo="propriedades"
        />
      </div>

      {erro && <div className="alert-error">{erro}</div>}
      {!dados && !erro && <p>Carregando...</p>}

      {dados && dados.linhas.length === 0 && <p className="empty-inline">Nenhuma propriedade para comparar.</p>}

      {dados && dados.linhas.length > 0 && (
        <div className="table-wrap">
          <table className="data-table data-table-fluida">
            <thead>
              <tr>
                <th>Propriedade</th>
                <th className="col-opcional">Cidade</th>
                <th>Animais</th>
                {dados.tipos.map((t) => (
                  <th key={t} className="valor col-opcional">
                    {t}
                  </th>
                ))}
                <th className="valor col-opcional">Veterinários</th>
                <th className="valor col-opcional">Usuários</th>
              </tr>
            </thead>
            <tbody>
              {dados.linhas.map((l) => (
                <tr key={l.propriedade_id}>
                  <td>
                    {l.nome}
                    <span className="valor-secundario"> {l.proprietario_nome}</span>
                  </td>
                  <td className="col-opcional">{l.cidade_uf}</td>
                  <td>
                    <span className="comparativo-celula">
                      <span className="bar-track">
                        <span
                          className="bar-fill"
                          style={{ width: `${Math.max((l.animais / maiorRebanho) * 100, 2)}%`, background: "var(--color-primary)" }}
                        />
                      </span>
                      <strong>{l.animais}</strong>
                    </span>
                  </td>
                  {dados.tipos.map((t) => (
                    <td key={t} className="valor col-opcional">
                      {l.por_tipo[t] ?? 0}
                    </td>
                  ))}
                  <td className="valor col-opcional">{l.veterinarios}</td>
                  <td className="valor col-opcional">{l.usuarios}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
