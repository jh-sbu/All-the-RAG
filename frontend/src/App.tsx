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
  const [sources, setSources] = useState<ISource[]>([
    // {
    //   number: 1,
    //   title: "Source Title 1",
    //   summary: "Brief summary of source 1.",
    //   url: "https://source1.com"
    // },
    // {
    //   number: 2,
    //   title: "Source Title 2",
    //   summary: "Brief summary of source 2.",
    //   url: "https://source2.com"
    // }
  ]);

  const [chats, setChats] = useState<IChatSession[]>([
    // {
    //   id: "db11010b-d2dd-429e-9a6d-09d672acad4f" as UUID,
    //   title: "Chat 1",
    //   messages: []
    // },
    // {
    //   id: "1cf97315-3d6d-4b85-9759-ffae5b70cc72" as UUID,
    //   title: "Chat 2",
    //   messages: []
    // }
  ]);

  const fetchChatHistory = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URI}/api/chat`);
      const data = await response.json();
      console.log('Chat history:', data);
      setChats(data.chats);
    } catch (error) {
      console.error('Error fetching chat history:', error);
    }
  };

  useEffect(() => {
    fetchChatHistory();
  }, []);

  const handleDeleteChat = (chatId: UUID) => {
    setChats((prevChats: IChatSession[]) => prevChats.filter((chat: IChatSession) => chat.id !== chatId));
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
