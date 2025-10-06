import React, { useState } from 'react';
import './App.css';
import Chatbot from './Components/Chatbot';
import PreviousChatsSidebar from './Components/PreviousChatsSidebar';
import SourcesSidebar from './Components/SourcesSidebar';
import { IChatSession } from './Models/ChatSession';
import { ISource } from './Models/Source';

const App: React.FC = () => {
  const [sources, setSources] = useState<ISource[]>([
    {
      number: 1,
      title: "Source Title 1",
      summary: "Brief summary of source 1.",
      url: "https://source1.com"
    },
    {
      number: 2,
      title: "Source Title 2",
      summary: "Brief summary of source 2.",
      url: "https://source2.com"
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
        <Chatbot onUpdateSources={setSources} />
      </div>
      <SourcesSidebar sources={sources} />
    </div>
  );
}

export default App;
