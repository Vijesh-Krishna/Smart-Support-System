// frontend/src/components/Sidebar.jsx
import { motion } from "framer-motion";
import { X, Trash2 } from "lucide-react";

export default function Sidebar({
  isOpen,
  onClose,
  chats,
  onSelectChat,
  onDeleteChat,
  onDeleteAllChats,
}) {
  // Handle single chat deletion
  const handleDeleteChat = (chatId) => {
    if (!window.confirm("Are you sure you want to delete this chat?")) return;
    onDeleteChat(chatId);
  };

  return (
    <motion.aside
      initial={{ x: -300 }}
      animate={{ x: isOpen ? 0 : -300 }}
      transition={{ duration: 0.3 }}
      className="fixed top-0 left-0 h-full w-64 bg-gray-900 text-gray-100 shadow-lg p-4 z-50 border-r border-gray-800"
    >
      {/* Close Sidebar */}
      <button
        onClick={onClose}
        className="mb-4 text-gray-400 hover:text-red-500 flex items-center space-x-2 transition-colors"
      >
        <X size={20} /> <span>Close</span>
      </button>

      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="font-semibold text-lg text-cyan-400 tracking-wide">
          Conversations
        </h2>
        <button
          onClick={onDeleteAllChats}
          className="text-sm text-red-500 hover:text-red-400 flex items-center space-x-1 transition-colors"
        >
          <Trash2 size={16} /> <span>Delete All</span>
        </button>
      </div>

      {/* Chat List */}
      <nav className="space-y-2">
        {chats.length > 0 ? (
          chats.map((chat) => (
            <div
              key={chat.id}
              className="flex justify-between items-center group"
            >
              <button
                onClick={() => onSelectChat(chat)}
                className="text-left px-3 py-2 rounded-md flex-1 bg-gray-800/40 hover:bg-gray-800 transition-colors"
              >
                <span className="truncate text-sm text-gray-200 group-hover:text-white">
                  {chat.title || "Untitled Chat"}
                </span>
              </button>
              <button
                onClick={() => handleDeleteChat(chat.id)}
                className="text-red-500 hover:text-red-400 px-2 transition-colors"
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))
        ) : (
          <p className="text-gray-500 text-sm mt-4">No chats yet</p>
        )}
      </nav>
    </motion.aside>
  );
}
