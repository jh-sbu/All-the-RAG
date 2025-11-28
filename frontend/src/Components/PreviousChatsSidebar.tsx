import React from 'react';
import ChatCard from './ChatCard';
import NewChatButton from './NewChatButton';
import './PreviousChatsSidebar.css';
import { IChatSession, UUID } from '../Models/ChatSession';
import { Session } from '@supabase/supabase-js';

interface PreviousChatsSidebarProps {
  chats: IChatSession[];
  onDeleteChat: (chatId: UUID) => void;
  onNewChat: () => void;
  onPreviousClick: (chatId: UUID) => void;
  session: Session | null;
}

const PreviousChatsSidebar: React.FC<PreviousChatsSidebarProps> = ({ chats, onDeleteChat, onNewChat, onPreviousClick, session }) => {
  return (
    <div className="previous-chats-sidebar">
      <NewChatButton onClick={onNewChat} />
      <h2>{session ? 'Previous Chats' : 'Log In to See Saved Chats'}</h2>
      {session && chats.map((chat) => (
        <ChatCard
          key={chat.id}
          title={chat.title}
          chatId={chat.id}
          onDelete={onDeleteChat}
          onClick={onPreviousClick}
        />
      ))}
    </div>
  );
};

export default PreviousChatsSidebar;
