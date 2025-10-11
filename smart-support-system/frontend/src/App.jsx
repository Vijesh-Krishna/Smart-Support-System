import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { useContext } from "react";
import { AuthContext } from "./context/AuthContext";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Chat from "./pages/Chat";
import Dashboard from "./pages/Dashboard";
import DetailedAnalytics from "./pages/DetailedAnalytics"; 


function ProtectedRoute({ children, allow }) {
  const { user, loading } = useContext(AuthContext);
  const location = useLocation();

  if (loading) return <div>Loading...</div>;

  if (!user) {
    return <Navigate to="/" state={{ from: location }} replace />;
  }

  // case-insensitive role check
  if (
    allow &&
    ![]
      .concat(allow)
      .some((a) => a.toLowerCase() === (user.role || "").toLowerCase())
  ) {
    return (
      <Navigate
        to={user.role?.toLowerCase() === "admin" ? "/dashboard" : "/chat"}
        replace
      />
    );
  }

  return children;
}

export default function App() {
  const { user, loading } = useContext(AuthContext);

  if (loading) return <div>Loading...</div>;

  return (
    <Routes>
      {/* ---------- PUBLIC ---------- */}
      <Route
        path="/"
        element={
          user ? (
            // Only redirect if user is exactly at "/"
            <Navigate
              to={user.role?.toLowerCase() === "admin" ? "/dashboard" : "/chat"}
              replace
            />
          ) : (
            <Login />
          )
        }
      />
      <Route
        path="/register"
        element={user ? <Navigate to="/" replace /> : <Register />}
      />

      {/* ---------- USER ---------- */}
      <Route
        path="/chat"
        element={
          <ProtectedRoute allow="user">
            <Chat />
          </ProtectedRoute>
        }
      />

      {/* ---------- ADMIN ---------- */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute allow="admin">
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/detailed-analytics"
        element={
          <ProtectedRoute allow="admin">
            <DetailedAnalytics />
          </ProtectedRoute>
        }
      />

      {/* ---------- FALLBACK ---------- */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
