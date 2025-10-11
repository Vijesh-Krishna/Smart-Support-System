// src/context/AuthContext.jsx
import { createContext, useState, useEffect } from "react";
import { jwtDecode } from "jwt-decode"; // ✅ FIXED import

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem("auth");
    if (stored) {
      try {
        const { token } = JSON.parse(stored);
        const decoded = jwtDecode(token); // ✅ updated
        setUser({
          username: decoded.sub,
          role: decoded.role,
          token,
        });
      } catch (err) {
        console.error("Invalid stored token", err);
        localStorage.removeItem("auth");
      }
    }
    setLoading(false);
  }, []);

  const login = ({ token }) => {
    const decoded = jwtDecode(token); // ✅ updated
    const newUser = {
      username: decoded.sub,
      role: decoded.role,
      token,
    };
    setUser(newUser);
    localStorage.setItem("auth", JSON.stringify({ token }));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("auth");
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
