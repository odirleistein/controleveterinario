import { ArrowRight, Scale } from "lucide-react";
import { Link } from "react-router-dom";
import VacaIcon from "../components/VacaIcon";
import { useAuth } from "../context/AuthContext";

/**
 * Ponto de partida do acesso: qual propriedade abrir. Depois de escolhida, tudo
 * o que a tela mostra e daquela propriedade. Aqui so aparecem as propriedades
 * a que o usuario tem acesso (a API ja devolve so essas).
 */
export default function EscolherPropriedadePage() {
  const { usuario, propriedade, propriedades, escolherPropriedade, podeEscrever } = useAuth();

  return (
    <div className="page">
      <div className="page-header">
        <h2>Escolha a propriedade</h2>
        {propriedades.length > 1 && (
          <Link to="/comparativo" className="btn-secondary btn-com-icone">
            <Scale size={16} />
            Comparar propriedades
          </Link>
        )}
      </div>
      <p className="subtitle">
        Olá, {usuario?.nome}. Tudo o que você vê a seguir é da propriedade que escolher.
      </p>

      {propriedades.length === 0 ? (
        <div className="card">
          <p>Você ainda não tem acesso a nenhuma propriedade.</p>
          <p className="empty-inline">
            {podeEscrever
              ? "Cadastre uma em Propriedades (menu Cadastros) e vincule o seu usuário a ela."
              : "Peça a um administrador para liberar o seu acesso."}
          </p>
        </div>
      ) : (
        <div className="propriedade-cards">
          {propriedades.map((p) => (
            <button
              key={p.id}
              type="button"
              className={p.id === propriedade?.id ? "propriedade-card atual" : "propriedade-card"}
              onClick={() => escolherPropriedade(p.id)}
            >
              <span className="propriedade-card-icone">
                <VacaIcon size={26} />
              </span>
              <span className="propriedade-card-nome">{p.nome}</span>
              <span className="propriedade-card-info">{p.proprietario_nome}</span>
              <span className="propriedade-card-info">{p.cidade_uf}</span>
              <ArrowRight size={16} className="propriedade-card-seta" />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
