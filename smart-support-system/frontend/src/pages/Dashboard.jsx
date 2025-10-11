// frontend/src/pages/Dashboard.jsx
import { useState, useEffect, useContext } from "react";
import { motion } from "framer-motion";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { FiInfo } from "react-icons/fi"; // Info icon from react-icons

export default function Dashboard() {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState({});
  const [error, setError] = useState("");

  const fetchProducts = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/admin/products_metadata", {
        headers: { Authorization: `Bearer ${user.token}` },
      });
      const data = await res.json();

      const updatedProducts = data.products.map((product) => {
        if (product.files && product.files.length > 0) {
          const uniqueFiles = [
            ...new Map(product.files.map((f) => [f.file_id, f])).values(),
          ];
          return {
            ...product,
            files: uniqueFiles,
            product_name: uniqueFiles[0]?.file_name || product.product_id,
          };
        }
        return product;
      });

      setProducts(updatedProducts);
    } catch (err) {
      console.error("Error fetching products", err);
      setError("Failed to load products");
    }
  };

  const fetchAnalytics = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/admin/analytics", {
        headers: { Authorization: `Bearer ${user.token}` },
      });
      const data = await res.json();
      setAnalytics(data);
    } catch (err) {
      console.error("Error fetching analytics", err);
    }
  };

  useEffect(() => {
    if (user) {
      fetchProducts();
      fetchAnalytics();
    }
  }, [user?.username]);

  const handleFileSelect = (e) => setSelectedFiles(Array.from(e.target.files));

  const handleUpload = async () => {
    if (!selectedFiles.length) return alert("Please select files to upload");

    const newProgress = {};
    for (let file of selectedFiles) newProgress[file.name] = 0;
    setUploadProgress({ ...newProgress });

    for (let file of selectedFiles) {
      const formData = new FormData();
      formData.append("file", file);

      await new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "http://127.0.0.1:8000/admin/upload");
        xhr.setRequestHeader("Authorization", `Bearer ${user.token}`);

        xhr.upload.onprogress = (event) => {
          if (event.lengthComputable) {
            setUploadProgress((prev) => ({
              ...prev,
              [file.name]: Math.round((event.loaded / event.total) * 100),
            }));
          }
        };

        xhr.onload = () => {
          if (xhr.status >= 200 && xhr.status < 300) resolve();
          else reject(xhr.responseText);
        };

        xhr.onerror = () => reject("Upload failed");
        xhr.send(formData);
      }).catch((err) => alert(`Error uploading ${file.name}: ${err}`));
    }

    alert("All files uploaded successfully!");
    setSelectedFiles([]);
    setUploadProgress({});
    fetchProducts();
  };

  const allFiles = products.flatMap((product) => product.files || []);

  const handleDelete = async (fileId) => {
    const file = allFiles.find((f) => f.file_id === fileId);
    const fileName = file ? file.file_name : fileId;

    try {
      const res = await fetch(`http://127.0.0.1:8000/admin/delete/${fileId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${user.token}` },
      });
      if (!res.ok) throw new Error("Delete failed");
      await res.json();
      alert(`File '${fileName}' deleted successfully`);
      fetchProducts();
    } catch (err) {
      console.error(err);
      alert("Delete failed");
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-950 text-gray-100 p-6 overflow-y-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-blue-600">
          Welcome Admin {user?.username || ""}
        </h2>
        <div className="flex space-x-2">
          <button
            onClick={() => navigate("/detailed-analytics")}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-500 transition-colors font-semibold"
          >
            Detailed Analytics
          </button>
          <button
            onClick={logout}
            className="bg-red-700 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors font-semibold"
          >
            Logout
          </button>
        </div>
      </div>

      {error && <p className="text-red-500 mb-4">{error}</p>}

      {/* Upload Section */}
      <div className="mb-6 bg-gray-900 shadow-2xl rounded-lg p-4 border border-gray-800">
        <div className="flex items-center mb-2">
          <h3 className="text-xl font-semibold text-blue-300 mr-2">
            Upload New Files
          </h3>
          {/* Info Icon with Tooltip */}
          <div className="relative group">
            <FiInfo className="text-blue-400 cursor-pointer" />
            <div className="absolute top-full mt-2 mb-2 w-64 p-3 bg-gray-800 text-gray-200 text-sm rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity z-10">
              <p>PDF Upload Prerequisites:</p>
              <ul className="list-disc list-inside ml-4 mt-1">
                <li>The file must be a valid PDF.</li>
                <li>The PDF should contain only textual content.</li>
                <li>
                  The PDF should include proper information with clear headings
                  to ensure better AI query suggestions.
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* ✅ Clean Upload Input (no “Choose File” text) */}
        <div className="flex items-center">
          {/* Hidden native input */}
          <input
            id="fileInput"
            type="file"
            multiple
            onChange={handleFileSelect}
            className="hidden"
          />

          {/* Custom clickable upload box */}
          <label
            htmlFor="fileInput"
            className="border border-gray-700 bg-gray-850 text-gray-200 p-2 rounded w-full cursor-pointer hover:border-blue-500 transition-colors relative"
          >
            {selectedFiles.length ? (
              <span>{selectedFiles.length} file(s) selected</span>
            ) : (
              <span className="text-gray-400">Upload Files</span>
            )}
          </label>

          {/* Upload button */}
          <button
            onClick={handleUpload}
            className="bg-blue-600 text-white px-4 py-2 ml-4 rounded-lg hover:bg-blue-500 transition-colors font-semibold"
          >
            Upload
          </button>
        </div>

        {/* Progress bars */}
        {Object.keys(uploadProgress).map((fileName) => (
          <div key={fileName} className="mt-2">
            <p className="text-sm">{fileName}</p>
            <div className="w-full bg-gray-800 h-3 rounded">
              <div
                className="bg-blue-500 h-3 rounded"
                style={{ width: `${uploadProgress[fileName]}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>

      {/* Uploaded Files */}
      <div className="mb-6 bg-gray-900 shadow-2xl rounded-lg p-4 border border-gray-800">
        <h3 className="text-xl font-semibold mb-2 text-blue-300">
          Uploaded Files
        </h3>
        {allFiles.length > 0 ? (
          <ul>
            {allFiles.map((file) => (
              <motion.li
                key={file.file_id}
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex justify-between items-center bg-gray-850 shadow-inner p-2 mb-2 rounded border border-gray-800 hover:border-blue-500 transition-colors"
              >
                <div>
                  <p className="font-medium text-gray-100">{file.file_name}</p>
                  <p className="text-sm text-gray-400">
                    Uploaded: {new Date(file.uploaded_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleDelete(file.file_id)}
                    className="bg-red-700 text-white px-3 py-1 rounded hover:bg-red-600 transition-colors font-semibold"
                  >
                    Delete
                  </button>
                </div>
              </motion.li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500">No files uploaded yet.</p>
        )}
      </div>

      {/* Analytics */}
      <h3 className="text-xl font-semibold mb-3 text-blue-300">Analytics</h3>
      {analytics ? (
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gray-900 shadow-2xl rounded-lg p-4 border border-gray-800"
        >
          <p>Total Users: {analytics.total_users}</p>
          <p>Failed Queries: {analytics.failed_queries.length}</p>

          <h4 className="font-semibold mt-4 text-blue-300">
            Queries per Product:
          </h4>
          <ul className="list-disc list-inside mt-2 text-gray-200 bg-gray-850 p-2 rounded border border-gray-800">
            {Object.entries(analytics.queries_per_product).map(
              ([product, count]) => (
                <li key={product}>
                  {product}: {count}
                </li>
              )
            )}
          </ul>
        </motion.div>
      ) : (
        <p className="text-gray-500">Loading analytics...</p>
      )}
    </div>
  );
}
