import React, { useState, useEffect } from 'react';
import './App.css';
import Chatbot from './Components/Chatbot';
import PreviousChatsSidebar from './Components/PreviousChatsSidebar';
import SourcesSidebar from './Components/SourcesSidebar';
import Login from './Components/Login';
import ProfileMenu from './Components/ProfileMenu';
import { IChatSession, UUID } from './Models/ChatSession';
import { ISource } from './Models/Source';
import { IMessage } from './Models/Message';
import { supabase } from './lib/supabase';
import { Session } from '@supabase/supabase-js';

const App: React.FC = () => {
  const [session, setSession] = useState<Session | null>(null);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [messages, setMessages] = useState<IMessage[]>([]);
  const [chatId, setChatId] = useState<UUID | "None">("None");
  const [sources, setSources] = useState<ISource[]>([]);

  const [chats, setChats] = useState<IChatSession[]>([]);

  const fetchChatHistory = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URI}/api/chat`);
      const data = await response.json();

      if (data && typeof data === "object" && 'chats' in data) {
        setChats(data.chats);
      }
    } catch (error) {
      console.error('Error fetching chat history:', error);
    }
  };

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      if (session) {
        setShowLoginModal(false);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  useEffect(() => {
    if (session) {
      fetchChatHistory();
    }
  }, [session]);

  const handleDeleteChat = (deleteId: UUID) => {
    setChats((prevChats: IChatSession[]) => prevChats.filter((chat: IChatSession) => chat.id !== deleteId));

    if (deleteId == chatId) {
      setMessages([]);
      setChatId("None");
      setSources([]);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setChatId("None");
    setSources([]);
  };

  const handlePreviousChat = async (chatId: UUID) => {
    console.debug(`User clicked on a previous chat: ${chatId}`);
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URI}/api/chat/${chatId}`);
      const data = await response.json();
      setMessages(data.messages);
    } catch (error) {
      console.error(`Error fetching messages for chat ${chatId}:`, error);
    }
  }

  return (
    <>
      <div className="container">
        <PreviousChatsSidebar
          chats={chats}
          onDeleteChat={handleDeleteChat}
          onNewChat={handleNewChat}
          onPreviousClick={handlePreviousChat}
          session={session}
        />
        <div className="main-content">
          <div className="header">
            <h1 className="app-title">All-the-RAG</h1>
            <ProfileMenu session={session} onLoginClick={() => setShowLoginModal(true)} />
          </div>
          <Chatbot
            messages={messages}
            setMessages={setMessages}
            chatId={chatId}
            setChatId={setChatId}
            onUpdateSources={setSources}
            onRefreshChats={fetchChatHistory}
            session={session}
          />
        </div>
        <SourcesSidebar sources={sources} />
      </div>

      {showLoginModal && (
        <div className="modal-overlay" onClick={() => setShowLoginModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setShowLoginModal(false)}>×</button>
            <Login />
          </div>
        </div>
      )}
    </>
  );
}

export default App;
