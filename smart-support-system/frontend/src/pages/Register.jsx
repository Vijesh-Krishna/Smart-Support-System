import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import StarButton from "../style/StarButton";

export default function Register() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");

    if (!username.trim() || !password.trim() || !confirmPassword.trim()) {
      setError("All fields are required.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: username.trim(), password: password.trim() }),
      });

      let data = {};
      try {
        data = await response.json();
      } catch {}

      if (!response.ok) {
        setError(data.detail || "Registration failed.");
        return;
      }

      alert("Registration successful! Please login.");
      navigate("/login");
    } catch (err) {
      console.error("Registration error:", err.message);
      setError("Network issue. Please try again.");
    }
  };

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-gradient-to-br from-gray-900 via-gray-800 to-gray-950 text-white">
      {/* App Name */}
      <h1 className="absolute top-10 w-full text-center text-5xl md:text-6xl font-calligraphy z-10">
        Smart Support System
      </h1>

      {/* Registration Form */}
      <form
        onSubmit={handleRegister}
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 p-8 rounded-xl z-20 bg-black/50 backdrop-blur-md shadow-lg"
      >
        <h2 className="text-2xl font-bold mb-6 text-center">Register</h2>

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
          className="w-full mb-4 p-3 border rounded-lg bg-transparent text-white border-white/40"
        />
        <input
          type="password"
          placeholder="Confirm Password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          className="w-full mb-6 p-3 border rounded-lg bg-transparent text-white border-white/40"
        />

        <StarButton as="button" type="submit" color="cyan" speed="3s" className="w-full mb-4">
          Register
        </StarButton>

        <div className="text-sm text-white mt-2 text-center">
          Already have an account?{" "}
          <Link to="/login" className="text-cyan-300 hover:underline">
            Login
          </Link>
        </div>
      </form>
    </div>
  );
}
