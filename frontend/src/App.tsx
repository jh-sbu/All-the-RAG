import React, { useState, useEffect } from 'react';
import './App.css';
import Chatbot from './Components/Chatbot';
import PreviousChatsSidebar from './Components/PreviousChatsSidebar';
import SourcesSidebar from './Components/SourcesSidebar';
import { IChatSession, UUID } from './Models/ChatSession';
import { ISource } from './Models/Source';
import { IMessage } from './Models/Message';

const App: React.FC = () => {
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
      // setChats(data.chats);
    } catch (error) {
      console.error('Error fetching chat history:', error);
    }
  };

  useEffect(() => {
    fetchChatHistory();
  }, []);

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
    <div className="container">
      <PreviousChatsSidebar chats={chats} onDeleteChat={handleDeleteChat} onNewChat={handleNewChat} onPreviousClick={handlePreviousChat} />
      <div className="main-content">
        <Chatbot
          messages={messages}
          setMessages={setMessages}
          chatId={chatId}
          setChatId={setChatId}
          onUpdateSources={setSources}
          onRefreshChats={fetchChatHistory}
        />
      </div>
      <SourcesSidebar sources={sources} />
    </div>
  );
}

export default App;
