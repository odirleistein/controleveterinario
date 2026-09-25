import { Component } from "react";

/**
 * Captura erro de renderização e mostra uma mensagem no lugar.
 *
 * Sem isto, um erro de JavaScript dentro de uma tela derruba a árvore inteira e
 * o usuário vê uma PÁGINA EM BRANCO, sem pista nenhuma do que houve - foi o que
 * aconteceu quando o relatório era trocado no seletor e o componente novo
 * recebia, por um instante, o resultado do relatório anterior.
 *
 * Precisa ser classe: só componente de classe tem componentDidCatch.
 */
export default class ErroNaTela extends Component {
  constructor(props) {
    super(props);
    this.state = { erro: null };
  }

  static getDerivedStateFromError(erro) {
    return { erro };
  }

  componentDidCatch(erro, informacao) {
    // Fica no console para quem for investigar, com a pilha de componentes.
    console.error("Erro na tela:", erro, informacao?.componentStack);
  }

  render() {
    if (!this.state.erro) return this.props.children;

    return (
      <div className="page">
        <div className="page-header">
          <h2>Algo quebrou nesta tela</h2>
        </div>
        <div className="alert-error">
          {this.state.erro?.message ?? "Erro desconhecido."}
        </div>
        <p className="rel-legenda">
          Os seus dados estão a salvo — o problema é na exibição. Tente voltar e abrir a tela de
          novo. Se continuar, a mensagem acima e o console do navegador (F12) dizem onde foi.
        </p>
        <div className="page-actions">
          <button
            type="button"
            className="btn-secondary"
            onClick={() => this.setState({ erro: null })}
          >
            Tentar de novo
          </button>
          <button type="button" className="btn-primary" onClick={() => window.location.reload()}>
            Recarregar a página
          </button>
        </div>
      </div>
    );
  }
}
