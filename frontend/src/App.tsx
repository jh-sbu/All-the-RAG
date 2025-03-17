import React from 'react';
import './App.css';
import Chatbot from './Chatbot';
import ChatCard from './ChatCard';
import SourceCard from './SourceCard';

const App: React.FC = () => {
  return (
    <div className="container">
      <div className="sidebar">
         <ChatCard title="New Chat" />
         <h2>Previous Chats</h2>
         <ChatCard title="Chat 1" />
         <ChatCard title="Chat 2" />
         <ChatCard title="Chat 3" />
      </div>
      <div className="main-content">
         <Chatbot />
      </div>
      <div className="sources-sidebar">
         <h2>Sources</h2>
         <SourceCard number={1} title="Source Title 1" summary="Brief summary of source 1." website="https://source1.com" />
         <SourceCard number={2} title="Source Title 2" summary="Brief summary of source 2." website="https://source2.com" />
      </div>
    </div>
  );
}

export default App;
