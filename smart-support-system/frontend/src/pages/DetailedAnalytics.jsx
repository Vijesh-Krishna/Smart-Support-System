// frontend/src/pages/DetailedAnalytics.jsx
import { useEffect, useState, useContext } from "react";
import { motion } from "framer-motion";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { AuthContext } from "../context/AuthContext";

export default function DetailedAnalytics() {
  const { user } = useContext(AuthContext);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isSmallScreen, setIsSmallScreen] = useState(false);

  const fetchAnalytics = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/admin/analytics", {
        headers: { Authorization: `Bearer ${user.token}` },
      });
      if (!res.ok) throw new Error("Failed to fetch analytics");
      const data = await res.json();
      setAnalytics(data);
    } catch (err) {
      setError(err.message || "Failed to fetch analytics");
    } finally {
      setLoading(false);
    }
  };

  const handleClearFailedQueries = async () => {
    if (!confirm("Are you sure you want to clear all failed queries?")) return;
    try {
      const res = await fetch(
        "http://127.0.0.1:8000/admin/analytics/clear_failed_queries",
        {
          method: "DELETE",
          headers: { Authorization: `Bearer ${user.token}` },
        }
      );
      if (!res.ok) throw new Error("Failed to clear failed queries");
      setAnalytics((prev) => ({ ...prev, failed_queries: [] }));
      alert("Failed queries cleared successfully!");
    } catch (err) {
      alert(err.message || "Error clearing failed queries");
    }
  };

  useEffect(() => {
    if (user) fetchAnalytics();

    const handleResize = () => {
      setIsSmallScreen(window.innerWidth < 768);
    };
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [user?.username]);

  if (loading)
    return (
      <p className="p-6 text-gray-400 font-medium">
        Loading detailed analytics...
      </p>
    );

  if (error)
    return <p className="p-6 text-red-600 font-medium">Error: {error}</p>;

  const chartData =
    analytics && analytics.queries_per_product
      ? Object.entries(analytics.queries_per_product).map(([product, count]) => ({
          product,
          count,
        }))
      : [];

  return (
    <div className="flex flex-col h-screen bg-gray-950 text-gray-100 p-6 overflow-y-auto">
      <h2 className="text-2xl font-bold mb-6 text-blue-400">
        📊 Detailed Analytics
      </h2>

      {analytics && (
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="bg-gray-900 shadow-2xl rounded-lg p-6 overflow-y-auto flex-1 border border-gray-800"
        >
          {/* General Overview */}
          <div className="mb-6 space-y-1 bg-gray-850 p-4 rounded border border-gray-800">
            <p>
              <strong className="text-blue-300">Total Users:</strong>{" "}
              {analytics.total_users}
            </p>
            <p>
              <strong className="text-blue-300">Total Failed Queries:</strong>{" "}
              {analytics.failed_queries.length}
            </p>
          </div>

          {/* Modern Animated Bar Chart with Hover Glow */}
          <div className="mb-8 bg-gray-850 p-4 rounded border border-gray-800 shadow-lg">
            <h3 className="text-lg font-semibold mb-4 text-blue-300">
              📈 Queries Per Product
            </h3>
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={320}>
                <BarChart
                  data={chartData}
                  margin={{ top: 20, right: 30, left: 10, bottom: 10 }}
                >
                  <defs>
                    <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.9} />
                      <stop offset="95%" stopColor="#2563eb" stopOpacity={0.3} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
                  <XAxis
                    dataKey="product"
                    tick={{ fill: "#e2e8f0", fontSize: 12 }}
                    tickLine={false}
                    hide={isSmallScreen}
                  />
                  <YAxis tick={{ fill: "#e2e8f0" }} tickLine={false} />
                  <Tooltip
                    cursor={{ fill: "rgba(59,130,246,0.1)" }}
                    contentStyle={{
                      backgroundColor: "#111827",
                      border: "1px solid #1f2937",
                      borderRadius: "8px",
                      color: "#f9fafb",
                    }}
                  />
                  <Bar
                    dataKey="count"
                    fill="url(#barGradient)"
                    radius={[10, 10, 0, 0]}
                    animationDuration={1200}
                    animationEasing="ease-out"
                    onMouseOver={(e) => (e.currentTarget.style.filter = "drop-shadow(0 0 10px #3b82f6)")}
                    onMouseOut={(e) => (e.currentTarget.style.filter = "none")}
                  />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-400">No queries recorded yet.</p>
            )}
          </div>

          {/* Queries Per Product List */}
          <div className="mb-6 bg-gray-850 p-4 rounded border border-gray-800">
            <h3 className="text-lg font-semibold mb-2 text-blue-300">
              🗂 Queries Per Product (List View)
            </h3>
            <ul className="list-disc list-inside text-gray-200 space-y-1">
              {Object.entries(analytics.queries_per_product).map(
                ([product, count]) => (
                  <li key={product}>
                    {product}:{" "}
                    <span className="font-bold text-blue-300">{count}</span>
                  </li>
                )
              )}
            </ul>
          </div>

          {/* Failed Queries Detailed */}
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-blue-300">
                ❌ Failed Queries (with Bot Responses)
              </h3>
              {analytics.failed_queries.length > 0 && (
                <button
                  onClick={handleClearFailedQueries}
                  className="bg-red-700 text-white px-3 py-1 rounded hover:bg-red-600 transition-colors font-semibold"
                >
                  Clear Failed Queries
                </button>
              )}
            </div>

            {analytics.failed_queries.length > 0 ? (
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {analytics.failed_queries.map((fq, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: index * 0.05 }}
                    className="p-4 border rounded bg-gray-850 border-gray-800 shadow-inner hover:shadow-lg hover:scale-[1.03] transition-all duration-300"
                  >
                    <p>
                      <strong className="text-blue-300">Product:</strong>{" "}
                      {fq.product_id}
                    </p>
                    <p>
                      <strong className="text-blue-300">User Query:</strong>{" "}
                      {fq.query}
                    </p>
                    <p className="text-red-500 font-medium">
                      <strong>Bot Answer:</strong> {fq.answer}
                    </p>
                  </motion.div>
                ))}
              </div>
            ) : (
              <p className="text-gray-400">No failed queries found.</p>
            )}
          </div>
        </motion.div>
      )}
    </div>
  );
}
