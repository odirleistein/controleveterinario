/**
 * Rosto de vaca em uma cor so (usa currentColor), no lugar dos icones do lucide,
 * que nao tem vaca: o foco do sistema e a producao leiteira. Aceita "size" e
 * "className" como os icones do lucide, entao entra em qualquer lugar deles.
 *
 * Olhos, focinho e narinas sao "recortes" na cor --vaca-detalhe (por padrao a cor
 * primaria, que e o fundo do brand-mark); onde o fundo for outro, defina a variavel.
 */
export default function VacaIcon({ size = 24, className }) {
  const detalhe = "var(--vaca-detalhe, var(--color-primary))";
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="currentColor"
      className={className}
      aria-hidden="true"
    >
      {/* chifres e orelhas */}
      <path d="M19 20 C13 18 11 12 12 8 C17 10 21 14 23 18 Z" />
      <path d="M45 20 C51 18 53 12 52 8 C47 10 43 14 41 18 Z" />
      <ellipse cx="11" cy="27" rx="8" ry="4.5" transform="rotate(-25 11 27)" />
      <ellipse cx="53" cy="27" rx="8" ry="4.5" transform="rotate(25 53 27)" />
      {/* cabeca: testa larga afinando ate o focinho */}
      <path d="M20 18 C24 15 40 15 44 18 C47 26 46 34 44 40 L42 56 C38 60 26 60 22 56 L20 40 C18 34 17 26 20 18 Z" />
      {/* recortes */}
      <circle cx="25" cy="29" r="2.6" fill={detalhe} />
      <circle cx="39" cy="29" r="2.6" fill={detalhe} />
      <path d="M22 44 C28 41 36 41 42 44" fill="none" stroke={detalhe} strokeWidth="1.6" strokeLinecap="round" />
      <ellipse cx="28" cy="51" rx="1.8" ry="2.6" fill={detalhe} />
      <ellipse cx="36" cy="51" rx="1.8" ry="2.6" fill={detalhe} />
    </svg>
  );
}
