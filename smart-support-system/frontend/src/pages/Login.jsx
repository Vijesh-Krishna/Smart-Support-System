import { useState, useContext } from "react";
import { useNavigate, Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { jwtDecode } from "jwt-decode";
import StarButton from "../style/StarButton";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    if (!username.trim() || !password.trim()) {
      setError("Please enter both username and password.");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: username.trim(),
          password: password.trim(),
        }),
      });

      let data = {};
      try {
        data = await response.json();
      } catch {}

      if (!response.ok) {
        setError(data.detail || "Invalid username or password.");
        setUsername("");
        setPassword("");
        return;
      }

      const token = data.access_token;
      login({ token });
      const decoded = jwtDecode(token);
      navigate(decoded?.role === "admin" ? "/dashboard" : "/chat", { replace: true });

      setUsername("");
      setPassword("");
    } catch (err) {
      console.error("Login request error:", err.message);
      setError("Network issue. Please try again.");
    }
  };

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-gradient-to-br from-gray-900 via-gray-800 to-gray-950 text-white">
      {/* App Name */}
      <h1 className="absolute top-10 w-full text-center text-5xl md:text-6xl font-calligraphy z-10">
        Smart Support System
      </h1>

      {/* Login Form */}
      <form
        onSubmit={handleLogin}
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 p-8 rounded-xl z-20 bg-black/50 backdrop-blur-md"
      >
        <h2 className="text-2xl font-bold mb-6 text-center">Login</h2>

        {error && (
          <p className="text-red-400 mb-4 text-center font-medium">{error}</p>
        )}

        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full mb-4 p-3 border rounded-lg bg-transparent text-white border-white/40"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full mb-6 p-3 border rounded-lg bg-transparent text-white border-white/40"
        />

        <StarButton as="button" type="submit" color="cyan" speed="3s" className="w-full mb-4">
          Login
        </StarButton>

        <div className="text-sm text-white mt-2 text-center">
          New user?{" "}
          <Link to="/register" className="text-cyan-300 hover:underline">
            Register
          </Link>
        </div>
      </form>
    </div>
  );
}
