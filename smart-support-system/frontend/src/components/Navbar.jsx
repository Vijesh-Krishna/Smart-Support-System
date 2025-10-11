import { motion } from "framer-motion"
import { MessageCircle, Upload } from "lucide-react"

export default function Navbar() {
  return (
    <motion.header
      initial={{ y: -60 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6, type: "spring" }}
      className="bg-white shadow-md px-6 py-3 flex justify-between items-center"
    >
      <h1 className="text-xl font-bold text-indigo-600">Smart Support System</h1>
      <div className="flex space-x-4">
        <button className="flex items-center space-x-2 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-xl transition">
          <Upload size={18} /> <span>Upload</span>
        </button>
        <button className="flex items-center space-x-2 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-xl transition">
          <MessageCircle size={18} /> <span>Chat</span>
        </button>
      </div>
    </motion.header>
  )
}
