import React from 'react';
import ChatCard from './ChatCard';
import './PreviousChatsSidebar.css';

const PreviousChatsSidebar: React.FC = () => {
  return (
    <div className="previous-chats-sidebar">
      <ChatCard title="New Chat" />
      <h2>Previous Chats</h2>
      <ChatCard title="Chat 1" />
      <ChatCard title="Chat 2" />
      <ChatCard title="Chat 3" />
    </div>
  );
};

export default PreviousChatsSidebar;
