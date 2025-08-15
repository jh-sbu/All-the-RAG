import React from 'react';
import ChatCard from './ChatCard';
import './PreviousChatsSidebar.css';
import { IChatSession } from '../Models/ChatSession';

interface PreviousChatsSidebarProps {
  chats: IChatSession[];
}

const PreviousChatsSidebar: React.FC<PreviousChatsSidebarProps> = ({ chats }) => {
  return (
    <div className="previous-chats-sidebar">
      <ChatCard title="New Chat" />
      <h2>Previous Chats</h2>
      {chats.map((chat) => (
        <ChatCard
          key={chat.chat_title}
          title={chat.chat_title}
        />
      ))}
    </div>
  );
};

export default PreviousChatsSidebar;
