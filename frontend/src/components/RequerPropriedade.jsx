import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

/**
 * Barreira das telas que so fazem sentido dentro de uma propriedade (animais,
 * visao geral...). Sem propriedade aberta, manda para a escolha - o acesso
 * comeca sempre por ela.
 */
export default function RequerPropriedade() {
  const { propriedade } = useAuth();
  if (!propriedade) return <Navigate to="/escolher-propriedade" replace />;
  return <Outlet />;
}
