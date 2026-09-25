import { useEffect, useState } from "react";
import api from "../api/client";
import { mensagemErro } from "../utils/erros";
import { semAcento } from "../utils/format";

/**
 * Janela para escolher, numa lista com busca, tudo o que fica vinculado a um
 * registro (animais de uma propriedade, propriedades de um veterinario...).
 *
 * "url" e o endpoint do vinculo: o GET devolve { ids } e o PUT recebe { ids } com
 * o conjunto completo. "resource" e a lista de onde saem as opcoes, e "rotulo"
 * monta o texto de cada uma.
 */
export default function VinculosModal({ titulo, url, resource, rotulo, somenteLeitura = false, onFechar }) {
  const [opcoes, setOpcoes] = useState([]);
  const [marcados, setMarcados] = useState(new Set());
  const [busca, setBusca] = useState("");
  const [carregando, setCarregando] = useState(true);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");

  useEffect(() => {
    Promise.all([api.get(`/${resource}/`), api.get(url)])
      .then(([lista, vinculos]) => {
        setOpcoes(lista.data.map((o) => ({ id: o.id, texto: rotulo(o) })));
        setMarcados(new Set(vinculos.data.ids));
      })
      .catch((err) => setErro(mensagemErro(err, "Erro ao carregar os vínculos.")))
      .finally(() => setCarregando(false));
    // A janela e montada de novo a cada abertura; url/resource nao mudam com ela aberta.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function alternar(id) {
    setMarcados((atual) => {
      const novo = new Set(atual);
      if (novo.has(id)) novo.delete(id);
      else novo.add(id);
      return novo;
    });
  }

  async function salvar() {
    setSalvando(true);
    setErro("");
    try {
      await api.put(url, { ids: [...marcados] });
      onFechar();
    } catch (err) {
      setErro(mensagemErro(err, "Erro ao salvar os vínculos."));
    } finally {
      setSalvando(false);
    }
  }

  const visiveis = busca.trim()
    ? opcoes.filter((o) => semAcento(o.texto).includes(semAcento(busca.trim())))
    : opcoes;

  return (
    <div className="modal-backdrop">
      <div className="modal">
        <h3>{titulo}</h3>
        {erro && <div className="alert-error">{erro}</div>}
        {carregando ? (
          <p>Carregando...</p>
        ) : (
          <>
            <input type="text" placeholder="Buscar..." value={busca} onChange={(e) => setBusca(e.target.value)} />
            <div className="vinculos-lista">
              {visiveis.length === 0 && <div className="empty-inline">Nada encontrado.</div>}
              {visiveis.map((o) => (
                <label key={o.id} className="vinculos-opcao">
                  <input
                    type="checkbox"
                    checked={marcados.has(o.id)}
                    disabled={somenteLeitura}
                    onChange={() => alternar(o.id)}
                  />
                  {o.texto}
                </label>
              ))}
            </div>
            <p className="empty-inline">{marcados.size} selecionado(s)</p>
          </>
        )}
        <div className="modal-actions">
          <button type="button" className="btn-secondary" onClick={onFechar}>
            {somenteLeitura ? "Fechar" : "Cancelar"}
          </button>
          {!somenteLeitura && (
            <button type="button" disabled={salvando || carregando} onClick={salvar}>
              {salvando ? "Salvando..." : "Salvar"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
