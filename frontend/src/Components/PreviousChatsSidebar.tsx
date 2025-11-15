import React from 'react';
import ChatCard from './ChatCard';
import NewChatButton from './NewChatButton';
import './PreviousChatsSidebar.css';
import { IChatSession, UUID } from '../Models/ChatSession';

interface PreviousChatsSidebarProps {
  chats: IChatSession[];
  onDeleteChat?: (chatId: UUID) => void;
  onNewChat: () => void;
}

const PreviousChatsSidebar: React.FC<PreviousChatsSidebarProps> = ({ chats, onDeleteChat, onNewChat }) => {
  return (
    <div className="previous-chats-sidebar">
      <NewChatButton onClick={onNewChat} />
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
