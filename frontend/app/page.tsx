"use client";
import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { Send, Paperclip, Plus, MessageSquare, Trash2, Menu, FileText } from "lucide-react";

export default function Home() {
  const [sessions, setSessions] = useState<{id: string, title: string}[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<{role: string, content: string}[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
        const res = await fetch("http://localhost:8000/sessions");
        const data = await res.json();
        setSessions(data);
    } catch(e) { console.error("Erreur chargement sessions", e); }
  };

  const loadHistory = async (sessionId: string) => {
      setLoading(true);
      try {
          const res = await fetch(`http://localhost:8000/history/${sessionId}`);
          const history = await res.json();
          setMessages(history);
          setCurrentSessionId(sessionId);
      } catch(e) { console.error("Erreur historique", e); }
      setLoading(false);
  };

  const createNewSession = async () => {
    const res = await fetch("http://localhost:8000/sessions/new", { method: "POST" });
    const data = await res.json();
    setSessions(prev => [...prev, { id: data.session_id, title: data.title }]);
    setCurrentSessionId(data.session_id);
    setMessages([]); 
  };

  // Gestion UPLOAD MULTIPLE
 
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    // 1. On capture les fichiers dans une variable locale stable
    const files = e.target.files; 

    // 2. On vérifie cette variable locale
    if (!files || files.length === 0 || !currentSessionId) return;
    
    const formData = new FormData();
    // 3. On utilise 'files' (et non e.target.files) pour la boucle
    Array.from(files).forEach((file) => {
        formData.append("files", file); 
    });

    // 4. Ici aussi, on utilise 'files.length'. Plus de ligne rouge !
    setMessages(prev => [...prev, { role: "system", content: `📥 Analyse de ${files.length} fichier(s) en cours...` }]);
    
    try {
      const res = await fetch(`http://localhost:8000/upload/${currentSessionId}`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      
      setSessions(prev => prev.map(s => s.id === currentSessionId ? {...s, title: data.title} : s));
      setMessages(prev => [...prev, { role: "system", content: `✅ ${data.message}` }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: "system", content: "❌ Erreur lors de l'upload." }]);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || !currentSessionId) return;
    const userMsg = input;
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`http://localhost:8000/chat/${currentSessionId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: userMsg }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: "assistant", content: data.response }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: "assistant", content: "Erreur de connexion." }]);
    }
    setLoading(false);
  };

  return (
    <div className="flex h-screen bg-[#343541] text-white font-sans">
      
      {/* SIDEBAR */}
      <aside className="w-[260px] bg-[#202123] p-2 flex flex-col border-r border-gray-700 hidden md:flex">
        <button 
          onClick={createNewSession}
          className="flex items-center gap-3 px-3 py-3 rounded-md border border-gray-600 hover:bg-[#2A2B32] transition text-sm mb-4 text-white"
        >
          <Plus size={16} />
          New chat
        </button>

        <div className="flex-1 overflow-y-auto space-y-2">
            <div className="text-xs font-semibold text-gray-500 px-3 py-2">Historique</div>
            {sessions.map(session => (
              <button
                key={session.id}
                onClick={() => loadHistory(session.id)}
                className={`w-full flex items-center gap-3 px-3 py-3 rounded-md text-sm transition overflow-hidden ${currentSessionId === session.id ? 'bg-[#343541]' : 'hover:bg-[#2A2B32]'}`}
              >
                <MessageSquare size={16} className="text-gray-400 min-w-[16px]" />
                <span className="truncate">{session.title}</span>
              </button>
            ))}
        </div>
        
        <div className="pt-2 border-t border-gray-700 px-3 py-3 flex items-center gap-3">
            <div className="w-8 h-8 bg-green-600 rounded-sm flex items-center justify-center font-bold">O</div>
            <div className="text-sm font-bold">Oumniya</div>
        </div>
      </aside>

      {/* MAIN ZONE */}
      <main className="flex-1 flex flex-col relative bg-[#343541]">
        <div className="md:hidden flex items-center justify-between p-4 border-b border-gray-700">
            <Menu />
            <span>AskMe RAG</span>
            <Plus onClick={createNewSession}/>
        </div>

        <div className="flex-1 overflow-y-auto w-full scroll-smooth">
          {messages.length === 0 ? (
             <div className="h-full flex flex-col items-center justify-center text-gray-400">
                <div className="bg-white/10 p-4 rounded-full mb-4"><MessageSquare size={32}/></div>
                <h2 className="text-2xl font-bold text-gray-200">Prêt à analyser vos documents</h2>
                <p className="mt-2 text-sm">Sélectionnez un ou plusieurs PDF pour commencer.</p>
             </div>
          ) : (
            <div className="flex flex-col pb-32">
              {messages.map((msg, i) => (
                <div key={i} className={`w-full border-b border-black/10 dark:border-gray-900/50 ${msg.role === 'assistant' ? 'bg-[#444654]' : ''}`}>
                  <div className="max-w-3xl mx-auto flex gap-6 p-4 md:py-6">
                    <div className={`w-8 h-8 rounded-sm flex items-center justify-center shrink-0 ${msg.role === 'assistant' ? 'bg-green-500' : (msg.role === 'system' ? 'bg-blue-500' : 'bg-purple-600')}`}>
                        {msg.role === 'assistant' ? 'AI' : (msg.role === 'system' ? '⚙️' : 'U')}
                    </div>
                    <div className="prose prose-invert min-w-full">
                       {msg.role === 'system' ? (
                           <span className="text-gray-300 italic text-sm">{msg.content}</span>
                       ) : (
                           <ReactMarkdown>{msg.content}</ReactMarkdown>
                       )}
                    </div>
                  </div>
                </div>
              ))}
              {loading && <div className="w-full bg-[#444654] p-4"><div className="max-w-3xl mx-auto animate-pulse">▋</div></div>}
            </div>
          )}
        </div>

        {/* INPUT ZONE */}
        <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-[#343541] via-[#343541] to-transparent pt-10 pb-6 px-4">
          <div className="max-w-3xl mx-auto bg-[#40414F] border border-gray-600 rounded-xl shadow-xl flex items-end p-3 relative">
            <button 
                onClick={() => fileInputRef.current?.click()}
                className="p-2 text-gray-400 hover:text-white transition rounded-md mr-2"
                title="Ajouter des fichiers"
            >
                <Paperclip size={20} />
            </button>
            {/* Ajout de l'attribut 'multiple' ici */}
            <input 
                type="file" 
                ref={fileInputRef} 
                className="hidden" 
                accept=".pdf" 
                multiple 
                onChange={handleFileUpload}
            />

            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if(e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
              placeholder="Posez une question..."
              className="flex-1 max-h-[200px] bg-transparent border-none focus:ring-0 text-white resize-none py-2 px-1 scrollbar-hide"
              rows={1}
            />
            <button 
                onClick={sendMessage}
                disabled={!input.trim() && !loading}
                className={`p-2 rounded-md transition ${input.trim() ? 'bg-[#19c37d] text-white' : 'text-gray-500'}`}
            >
                <Send size={16} />
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}