import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute() {
  const { usuario, carregando } = useAuth();
  const location = useLocation();

  if (carregando) {
    return <div className="loading-screen">Carregando...</div>;
  }
  if (!usuario) {
    // Guarda o link pedido: depois do login o Login.jsx volta para ele.
    const from = location.pathname + location.search;
    return <Navigate to="/login" replace state={{ from }} />;
  }
  return <Outlet />;
}
