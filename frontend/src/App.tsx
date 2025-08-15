import React, { useState } from 'react';
import './App.css';
import Chatbot from './Components/Chatbot';
import PreviousChatsSidebar from './Components/PreviousChatsSidebar';
import SourcesSidebar from './Components/SourcesSidebar';
import { IChatSession } from './Models/ChatSession';

const App: React.FC = () => {
  const [sources, _setSources] = useState([
    {
      number: 1,
      title: "Source Title 1",
      summary: "Brief summary of source 1.",
      website: "https://source1.com"
    },
    {
      number: 2,
      title: "Source Title 2",
      summary: "Brief summary of source 2.",
      website: "https://source2.com"
    }
  ]);

  const [chats, _setChats] = useState<IChatSession[]>([
    {
      chat_title: "Chat 1",
      messages: []
    },
    {
      chat_title: "Chat 2",
      messages: []
    }
  ]);

  return (
    <div className="container">
      <PreviousChatsSidebar chats={chats} />
      <div className="main-content">
        <Chatbot />
      </div>
      <SourcesSidebar sources={sources} />
    </div>
  );
}

export default App;
