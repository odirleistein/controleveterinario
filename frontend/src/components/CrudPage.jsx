import { Pencil, Plus, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";
import CepInput from "./CepInput";
import LocalEnderecoField from "./LocalEnderecoField";
import MultiSelect from "./MultiSelect";
import Pagination from "./Pagination";
import SearchableSelect from "./SearchableSelect";
import TelefonesField from "./TelefonesField";
import { semAcento } from "../utils/format";

/** Campo com "mostrarSe" so entra no formulario (e no payload) quando a funcao devolve true. */
function campoAtivoNoForm(f, dados) {
  return !f.mostrarSe || f.mostrarSe(dados);
}

function valorInicial(fields) {
  const vazio = {};
  fields.forEach((f) => {
    vazio[f.name] = f.default ?? (f.type === "checkbox" ? false : f.type === "multiselect" ? [] : "");
  });
  return vazio;
}

function montarPayload(fields, dados, ehEdicao) {
  const payload = {};
  camposVisiveis(fields, ehEdicao).forEach((f) => {
    if (!campoAtivoNoForm(f, dados)) return;
    let v = dados[f.name];
    if (f.serializar) {
      // Campo composto (ex.: bairro/localidade): um controle so, varias chaves no payload.
      Object.assign(payload, f.serializar(v));
      return;
    }
    if (f.type === "multiselect") {
      v = (v ?? []).map(Number);
    } else if (f.type === "telefones") {
      // Linha sem numero e so uma linha em branco esquecida no formulario.
      v = (v ?? []).filter((t) => t.numero?.trim());
    } else if (f.type === "number" || f.isId) {
      v = v === "" || v === null || v === undefined ? null : Number(v);
    } else if (f.type !== "checkbox" && v === "") {
      // campo de texto/data opcional em branco -> null (nao string vazia),
      // para nao colidir com indices unicos parciais (que ignoram NULL)
      v = null;
    }
    payload[f.name] = v;
  });
  return payload;
}

/**
 * Campos com "somenteNovo" (ex.: senha) so aparecem - e so sao enviados - na
 * criacao. "somenteEdicao" e o oposto (ex.: imagem, que precisa de um id para
 * ter para onde subir e por isso nao faz sentido no formulario de criacao).
 */
function camposVisiveis(fields, ehEdicao) {
  return fields.filter((f) => (ehEdicao ? !f.somenteNovo : !f.somenteEdicao));
}

/** Colunas marcadas com "opcional" somem em telas estreitas, via CSS. */
function classeColuna(coluna) {
  return [coluna.align === "right" ? "valor" : "", coluna.opcional ? "col-opcional" : ""]
    .filter(Boolean)
    .join(" ");
}

/**
 * Tela de cadastro generica (tabela + formulario em modal) reaproveitada
 * pelas entidades simples da API: contas, pessoas, categorias, veiculos,
 * despesas recorrentes, tags. Campos "select" podem trazer as opcoes prontas
 * (options) ou buscar de outro recurso da API (optionsResource + labelKey).
 *
 * Filtros (opcionais, aplicados no lado do cliente sobre a lista carregada):
 *   - campoBusca: nome do campo pesquisado por um input de texto livre.
 *   - filtrosExtras: [{ campo, label, opcoes: [{value,label}] }] - selects extras.
 *   - se algum field for um checkbox "ativo"/"ativa", ganha filtro Ativos/Inativos automatico.
 *
 * Um field marcado com "somenteNovo" (ex.: a senha em Usuarios) aparece apenas no
 * formulario de criacao e nao entra no payload do PUT.
 *
 * Responsividade: uma coluna marcada com "opcional" some abaixo de 900px, e a prop
 * "larga" libera a pagina do limite de 1280px (so vale a pena em tabelas densas).
 *
 * Tipos de campo alem dos nativos do <input>: "select", "checkbox", "textarea",
 * "cep" (mascara + confere o cadastro de CEPs), "telefones" (lista de contatos
 * com um principal), "multiselect" (lista de ids escolhidos em varias opcoes) e
 * "local-endereco" (bairro ou localidade entre os que o CEP do form cobre). Um campo
 * composto declara "carregar(item)" (valor do controle a partir do registro) e
 * "serializar(valor)" (objeto que entra no payload). Um campo com "mostrarSe(dados)" some quando a funcao devolve
 * false (ex.: CPF so para pessoa fisica). Um select/multiselect pode ter
 * "optionsFilter(opcao, dadosDoForm)" para recortar a lista carregada (ex.: so os
 * bairros da cidade escolhida) e "limpaAoMudar: [campos]" para zerar campos que
 * dependem dele quando ele muda. "largo" abre o modal em duas colunas.
 *
 * Quem so tem perfil de consulta (VISUALIZADOR) nao ve Novo/Editar/Remover.
 */
export default function CrudPage({
  resource,
  title,
  fields,
  columns,
  extraActions,
  campoBusca,
  filtrosExtras = [],
  larga = false,
  largo = false,
}) {
  const { podeEscrever } = useAuth();
  const [itens, setItens] = useState([]);
  const [referencias, setReferencias] = useState({});
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [editando, setEditando] = useState(null);
  const [salvando, setSalvando] = useState(false);

  const [busca, setBusca] = useState("");
  const [filtroAtivo, setFiltroAtivo] = useState("");
  const [valoresFiltrosExtras, setValoresFiltrosExtras] = useState({});

  const [pagina, setPagina] = useState(1);
  const [itensPorPagina, setItensPorPagina] = useState(20);

  const campoAtivo = fields.find((f) => f.type === "checkbox" && (f.name === "ativo" || f.name === "ativa"))?.name;

  useEffect(() => {
    const recursos = [...new Set(fields.filter((f) => f.optionsResource).map((f) => f.optionsResource))];
    if (recursos.length === 0) return;
    Promise.all(recursos.map((r) => api.get(`/${r}/`).then((res) => [r, res.data]))).then((pares) =>
      setReferencias(Object.fromEntries(pares)),
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resource]);

  async function carregar() {
    setCarregando(true);
    setErro("");
    try {
      const res = await api.get(`/${resource}/`);
      setItens(res.data);
    } catch {
      setErro("Erro ao carregar dados.");
    } finally {
      setCarregando(false);
    }
  }

  useEffect(() => {
    carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resource]);

  function abrirNovo() {
    setErro("");
    setEditando(valorInicial(fields));
  }

  function abrirEdicao(item) {
    setErro("");
    const composto = Object.fromEntries(
      fields.filter((f) => f.carregar).map((f) => [f.name, f.carregar(item)]),
    );
    setEditando({ ...item, ...composto });
  }

  async function salvar(e) {
    e.preventDefault();
    setSalvando(true);
    setErro("");
    try {
      const payload = montarPayload(fields, editando, Boolean(editando.id));
      if (editando.id) {
        await api.put(`/${resource}/${editando.id}`, payload);
      } else {
        await api.post(`/${resource}/`, payload);
      }
      setEditando(null);
      await carregar();
    } catch (err) {
      setErro(String(err.response?.data?.detail ?? "Erro ao salvar."));
    } finally {
      setSalvando(false);
    }
  }

  async function remover(item) {
    const rotulo = item[columns[0].key];
    if (!window.confirm(`Remover "${rotulo}"?`)) return;
    setErro("");
    try {
      await api.delete(`/${resource}/${item.id}`);
      await carregar();
    } catch {
      setErro("Erro ao remover.");
    }
  }

  function opcoesDoCampo(f) {
    if (f.options) return f.options.map((o) => ({ value: o.value, label: o.label }));
    let lista = referencias[f.optionsResource] ?? [];
    // Campo auto-referente (ex.: categoria pai) nao pode listar o proprio registro em edicao.
    if (f.optionsResource === resource && editando?.id) {
      lista = lista.filter((o) => o.id !== editando.id);
    }
    if (f.optionsFilter) {
      // Na edicao, o valor ja gravado continua na lista mesmo que o filtro o exclua hoje.
      lista = lista.filter((o) => f.optionsFilter(o, editando) || String(o.id) === String(editando?.[f.name]));
    }
    return lista.map((o) => ({ value: o.id, label: o[f.labelKey ?? "nome"] }));
  }

  const itensFiltrados = itens.filter((item) => {
    if (campoBusca && busca.trim() && !semAcento(item[campoBusca]).includes(semAcento(busca.trim()))) {
      return false;
    }
    if (campoAtivo && filtroAtivo !== "" && String(!!item[campoAtivo]) !== filtroAtivo) {
      return false;
    }
    for (const fe of filtrosExtras) {
      const v = valoresFiltrosExtras[fe.campo];
      if (v && String(item[fe.campo] ?? "") !== String(v)) return false;
    }
    return true;
  });

  const temFiltros = Boolean(campoBusca) || Boolean(campoAtivo) || filtrosExtras.length > 0;

  useEffect(() => {
    setPagina(1);
  }, [busca, filtroAtivo, valoresFiltrosExtras, resource]);

  const totalPaginas = Math.max(1, Math.ceil(itensFiltrados.length / itensPorPagina));
  const paginaAtual = Math.min(pagina, totalPaginas);
  const itensPaginados = itensFiltrados.slice(
    (paginaAtual - 1) * itensPorPagina,
    paginaAtual * itensPorPagina,
  );

  return (
    <div className={larga ? "page page-larga" : "page"}>
      <div className="page-header">
        <h2>{title}</h2>
        {podeEscrever && (
          <button type="button" className="btn-primary" onClick={abrirNovo}>
            <Plus size={16} />
            Novo
          </button>
        )}
      </div>

      {temFiltros && (
        <div className="filtros">
          {campoBusca && (
            <input
              type="text"
              placeholder="Buscar..."
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
            />
          )}
          {filtrosExtras.map((fe) => (
            <select
              key={fe.campo}
              value={valoresFiltrosExtras[fe.campo] ?? ""}
              onChange={(e) => setValoresFiltrosExtras((prev) => ({ ...prev, [fe.campo]: e.target.value }))}
            >
              <option value="">{fe.label}</option>
              {fe.opcoes.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          ))}
          {campoAtivo && (
            <select value={filtroAtivo} onChange={(e) => setFiltroAtivo(e.target.value)}>
              <option value="">Ativos e inativos</option>
              <option value="true">Somente ativos</option>
              <option value="false">Somente inativos</option>
            </select>
          )}
        </div>
      )}

      {erro && !editando && <div className="alert-error">{erro}</div>}

      {carregando ? (
        <p>Carregando...</p>
      ) : (
        <div className="table-wrap">
        <table className="data-table data-table-fluida">
          <thead>
            <tr>
              {columns.map((c) => (
                <th key={c.key} className={classeColuna(c)}>{c.label}</th>
              ))}
              <th />
            </tr>
          </thead>
          <tbody>
            {itensPaginados.map((item) => (
              <tr key={item.id}>
                {columns.map((c) => (
                  <td key={c.key} className={classeColuna(c)}>
                    {c.render ? c.render(item[c.key], item) : String(item[c.key] ?? "-")}
                  </td>
                ))}
                <td className="actions">
                  {extraActions?.(item, { reload: carregar })}
                  {podeEscrever && (
                    <>
                      <button type="button" className="icon-btn" title="Editar" onClick={() => abrirEdicao(item)}>
                        <Pencil size={15} />
                      </button>
                      <button type="button" className="icon-btn danger" title="Remover" onClick={() => remover(item)}>
                        <Trash2 size={15} />
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
            {itensFiltrados.length === 0 && (
              <tr>
                <td colSpan={columns.length + 1} className="empty">
                  {itens.length === 0 ? "Nenhum registro encontrado." : "Nenhum registro corresponde ao filtro."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
        </div>
      )}

      {!carregando && (
        <Pagination
          pagina={paginaAtual}
          totalItens={itensFiltrados.length}
          itensPorPagina={itensPorPagina}
          onMudarPagina={setPagina}
          onMudarItensPorPagina={(n) => {
            setItensPorPagina(n);
            setPagina(1);
          }}
        />
      )}

      {editando && (
        <div className="modal-backdrop">
          <form className={largo ? "modal modal-largo" : "modal"} onSubmit={salvar}>
            <h3>
              {editando.id ? "Editar" : "Novo"} — {title}
            </h3>
            {erro && <div className="alert-error">{erro}</div>}
            {camposVisiveis(fields, Boolean(editando.id))
              .filter((f) => campoAtivoNoForm(f, editando))
              .map((f) => {
              // MultiSelect tem checkboxes e um botao proprios: dentro de um <label> o clique
              // numa opcao seria repassado ao botao e fecharia a lista. Por isso um <div>.
              const Campo = f.type === "multiselect" ? "div" : "label";
              return (
              <Campo key={f.name} className={f.type === "multiselect" ? "campo-multiplo" : undefined}>
                {f.label}
                {f.type === "select" ? (
                  <SearchableSelect
                    value={editando[f.name] ?? ""}
                    onChange={(valor) => {
                      const dependentes = Object.fromEntries((f.limpaAoMudar ?? []).map((nome) => [nome, []]));
                      setEditando({ ...editando, [f.name]: valor, ...dependentes });
                    }}
                    options={opcoesDoCampo(f)}
                    allowEmpty={!f.required}
                    emptyLabel="Nenhuma"
                    required={f.required}
                  />
                ) : f.type === "checkbox" ? (
                  <input
                    type="checkbox"
                    checked={!!editando[f.name]}
                    onChange={(e) => setEditando({ ...editando, [f.name]: e.target.checked })}
                  />
                ) : f.type === "local-endereco" ? (
                  <LocalEnderecoField
                    cep={editando[f.campoCep ?? "cep"]}
                    value={editando[f.name] ?? ""}
                    onChange={(valor) => setEditando((atual) => ({ ...atual, [f.name]: valor }))}
                  />
                ) : f.type === "multiselect" ? (
                  <MultiSelect
                    value={editando[f.name] ?? []}
                    onChange={(valor) => setEditando({ ...editando, [f.name]: valor })}
                    options={opcoesDoCampo(f)}
                    todasLabel={f.vazioLabel ?? "Nenhum"}
                    nomeMultiplo={f.nomeMultiplo ?? "selecionados"}
                  />
                ) : f.type === "cep" ? (
                  <CepInput
                    value={editando[f.name] ?? ""}
                    onChange={(valor) => setEditando({ ...editando, [f.name]: valor })}
                    required={f.required}
                  />
                ) : f.type === "telefones" ? (
                  <TelefonesField
                    value={editando[f.name] ?? []}
                    onChange={(valor) => setEditando({ ...editando, [f.name]: valor })}
                  />
                ) : f.type === "textarea" ? (
                  <textarea
                    value={editando[f.name] ?? ""}
                    onChange={(e) => setEditando({ ...editando, [f.name]: e.target.value })}
                  />
                ) : (
                  <input
                    type={f.type ?? "text"}
                    value={editando[f.name] ?? ""}
                    onChange={(e) => setEditando({ ...editando, [f.name]: e.target.value })}
                    required={f.required}
                    step={f.type === "number" ? "0.01" : undefined}
                  />
                )}
              </Campo>
              );
            })}
            <div className="modal-actions">
              <button
                type="button"
                className="btn-secondary"
                onClick={() => {
                  setEditando(null);
                  setErro("");
                }}
              >
                Cancelar
              </button>
              <button type="submit" disabled={salvando}>
                {salvando ? "Salvando..." : "Salvar"}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
