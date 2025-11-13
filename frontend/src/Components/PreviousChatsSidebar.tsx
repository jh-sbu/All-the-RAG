import React from 'react';
import ChatCard from './ChatCard';
import './PreviousChatsSidebar.css';
import { IChatSession, UUID } from '../Models/ChatSession';

interface PreviousChatsSidebarProps {
  chats: IChatSession[];
  onDeleteChat?: (chatId: UUID) => void;
}

const PreviousChatsSidebar: React.FC<PreviousChatsSidebarProps> = ({ chats, onDeleteChat }) => {
  return (
    <div className="previous-chats-sidebar">
      <ChatCard title="New Chat" />
      <h2>Previous Chats</h2>
      {chats.map((chat) => (
        <ChatCard
          key={chat.id}
          title={chat.title}
          chatId={chat.id}
          onDelete={onDeleteChat}
        />
      ))}
    </div>
  );
};

export default PreviousChatsSidebar;
