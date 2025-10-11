import { useState, useEffect, useContext, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import Sidebar from "../components/Sidebar";
import api from "../utils/api";
import { AuthContext } from "../context/AuthContext";
import StarButton from "../style/StarButton";

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [selectedProduct, setSelectedProduct] = useState("");
  const [products, setProducts] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [chats, setChats] = useState([]);
  const [currentChat, setCurrentChat] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [toasts, setToasts] = useState([]);
  const [botTyping, setBotTyping] = useState(false);

  const { user, logout } = useContext(AuthContext);
  const messagesEndRef = useRef(null);

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, botTyping]);

  // Fetch products
  useEffect(() => {
    if (!user) return;
    api.get("/users/products", { headers: { Authorization: `Bearer ${user.token}` } })
      .then(res => setProducts(res.data.products || []))
      .catch(() => showToast("Failed to load products. Please refresh.", "error"));
  }, [user]);

  // Fetch chats
  useEffect(() => {
    if (!user) return;
    const fetchChats = async () => {
      try {
        const res = await api.get("/chat/all", { headers: { Authorization: `Bearer ${user.token}` } });
        const allChats = res.data || [];
        setChats(allChats);
        if (allChats.length > 0) {
          const latest = allChats[allChats.length - 1];
          setCurrentChat(latest);
          setMessages(latest.messages);
        } else {
          await startNewChat(false);
        }
      } catch {
        showToast("Failed to fetch chats. Starting a new chat.", "error");
        await startNewChat(false);
      }
    };
    fetchChats();
  }, [user]);

  // Fetch suggestions
  useEffect(() => {
    if (!selectedProduct || !user) return;
    api.get(`/chat/${selectedProduct}/suggestions`, { headers: { Authorization: `Bearer ${user.token}` } })
      .then(res => setSuggestions(res.data.suggestions || []))
      .catch(() => setSuggestions([]));
  }, [selectedProduct, user]);

  // Toast helper
  const showToast = (message, type = "info") => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 3000);
  };

  const startNewChat = async (saveCurrent = true) => {
    try {
      if (saveCurrent && currentChat?.messages.length > 0) {
        setChats(prev => prev.map(chat => chat.id === currentChat.id ? currentChat : chat));
      }
      const res = await api.post("/chat/new", {}, { headers: { Authorization: `Bearer ${user.token}` } });
      setChats(prev => [...prev, res.data]);
      setCurrentChat(res.data);
      setMessages([{
        sender: "bot",
        text: `Hi ${user.username || "there"} 👋, this is a new chat!`,
        timestamp: new Date().toISOString(),
      }]);
      setSelectedProduct("");
      setSuggestions([]);
    } catch {
      showToast("Failed to start a new chat. Try again later.", "error");
    }
  };

  const selectChat = async chat => {
    try {
      const res = await api.get(`/chat/${chat.id}`, { headers: { Authorization: `Bearer ${user.token}` } });
      setCurrentChat(res.data);
      setMessages(res.data.messages);
    } catch {
      setCurrentChat(chat);
      setMessages(chat.messages);
      showToast("Failed to load selected chat. Showing cached messages.", "error");
    }
    setSidebarOpen(false);
  };

  const deleteChat = async chatId => {
    if (!window.confirm("Are you sure you want to delete this chat?")) return;
    try {
      await api.delete(`/chat/${chatId}`, { headers: { Authorization: `Bearer ${user.token}` } });
      const remainingChats = chats.filter(c => c.id !== chatId);
      setChats(remainingChats);
      if (currentChat?.id === chatId) {
        if (remainingChats.length > 0) {
          const latest = remainingChats[remainingChats.length - 1];
          setCurrentChat(latest);
          setMessages(latest.messages);
        } else {
          await startNewChat(false);
        }
      }
    } catch {
      showToast("Failed to delete chat. Try again.", "error");
    }
  };

  const deleteAllChats = async () => {
    if (!window.confirm("Are you sure you want to delete all chats?")) return;
    try {
      await api.delete("/chat/history", { headers: { Authorization: `Bearer ${user.token}` } });
      setChats([]);
      setCurrentChat(null);
      setMessages([]);
      await startNewChat(false);
    } catch {
      showToast("Failed to delete all chats. Try again.", "error");
    }
  };

  const handleSuggestionClick = s => {
    sendMessage(s);
    setSuggestions([]);
  };

  const sendMessage = async customInput => {
    const question = customInput || input;

    // Validation
    if (!question.trim()) return showToast("Please enter a question before sending.", "error");
    if (!selectedProduct) return showToast("Please select a product before sending.", "error");
    if (!currentChat) return showToast("No active chat found. Please start a new chat.", "error");

    setInput("");

    // Append user message
    const userMessage = {
      sender: "user",
      text: question,
      timestamp: new Date().toISOString(),
      product_id: selectedProduct,
      sources: []
    };
    setMessages(prev => [...prev, userMessage]);

    // Show bot typing
    setBotTyping(true);

    try {
      const res = await api.post(
        `/chat/${currentChat.id}/message`,
        { chat_id: currentChat.id, product_id: selectedProduct, question },
        { headers: { Authorization: `Bearer ${user.token}` } }
      );

      const serverMessages = res.data.messages || [];
      setMessages(serverMessages);

      if (res.data?.id) {
        setChats(prev => prev.map(chat => chat.id === res.data.id ? res.data : chat));
        setCurrentChat(res.data);
      }
    } catch {
      showToast("Failed to send message. Try again later.", "error");
    } finally {
      setBotTyping(false);
    }
  };

  const handleKeyDown = e => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatLocalTime = utcTimestamp => {
    if (!utcTimestamp) return "";
    const utcDate = new Date(utcTimestamp);
    const istDate = new Date(utcDate.getTime() + 5.5 * 60 * 60 * 1000);
    return istDate.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: true });
  };

  return (
    <div className="flex h-screen bg-black text-white">
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        chats={chats}
        onSelectChat={selectChat}
        onDeleteChat={deleteChat}
        onDeleteAllChats={deleteAllChats}
      />

      <div className="flex flex-col flex-1 relative">
        {/* Header */}
        <div className="flex justify-between items-center p-4 bg-gray-900 border-b border-gray-700">
          <div className="flex items-center space-x-3">
            <button onClick={() => setSidebarOpen(true)} className="text-2xl font-bold bg-gray-800 px-3 py-1 rounded">
              ☰
            </button>
            <h1 className="text-lg font-semibold">Smart Support System</h1>
          </div>
          <div className="flex space-x-2">
            <StarButton as="button" onClick={() => startNewChat(true)} color="cyan" speed="3s" thickness={2} className="px-2 py-1 text-sm">
              New Chat
            </StarButton>
            <StarButton as="button" onClick={logout} color="cyan" speed="3s" thickness={2} className="px-2 py-1 text-sm">
              Logout
            </StarButton>
          </div>
        </div>

        {/* Chat messages */}
        <div className="flex-1 overflow-y-auto p-4 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-950">
          {messages.map((m, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: m.sender === "user" ? 50 : -50 }}
              animate={{ opacity: 1, x: 0 }}
              className={`mb-2 p-3 rounded-xl max-w-xs break-words ${m.sender === "user" ? "bg-blue-600 text-white ml-auto" : "bg-black text-blue-100 mr-auto"}`}
            >
              <ReactMarkdown>{m.text}</ReactMarkdown>
              <p className="text-xs text-blue-200 mt-1 text-right">{formatLocalTime(m.timestamp)}</p>
            </motion.div>
          ))}

          {botTyping && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mb-2 p-3 rounded-xl max-w-xs bg-blue-900 mr-auto italic text-blue-200">
              Bot is typing...
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggestions */}
        <AnimatePresence>
          {suggestions.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="absolute bottom-20 left-0 right-0 px-4 flex flex-wrap justify-center gap-2 z-10"
            >
              {suggestions.map((s, idx) => (
                <motion.button
                  key={idx}
                  whileHover={{ scale: 1.05 }}
                  onClick={() => handleSuggestionClick(s)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-full text-sm shadow hover:bg-blue-700 transition"
                >
                  {s}
                </motion.button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Input area */}
        <div className="p-3 flex items-center space-x-2 border-t border-gray-700 bg-gray-900 relative z-20">
          <select
            className="border rounded p-2 h-12 bg-gray-800 text-white border-gray-600"
            value={selectedProduct}
            onChange={e => setSelectedProduct(e.target.value)}
          >
            <option value="">Select product</option>
            {products.length > 0
              ? products.map(pid => <option key={pid} value={pid}>{pid}</option>)
              : <option disabled>Loading products...</option>}
          </select>

          <input
            className="flex-1 border rounded p-2 h-12 bg-gray-800 text-white border-gray-600"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask something..."
          />

          <button onClick={() => sendMessage()} className="bg-blue-700 hover:bg-blue-600 text-white px-6 rounded h-12">
            Send
          </button>
        </div>

        {/* Toast notifications */}
        <div className="fixed top-4 right-4 flex flex-col gap-2 z-50">
          <AnimatePresence>
            {toasts.map(t => (
              <motion.div
                key={t.id}
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 50 }}
                className={`px-4 py-2 rounded shadow-lg text-white ${t.type === "error" ? "bg-red-500" : "bg-blue-500"}`}
              >
                {t.message}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
