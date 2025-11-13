import './ChatCard.css';
import { UUID } from '../Models/ChatSession';

interface ChatCardProps {
  title: string;
  chatId?: UUID;
  onDelete?: (chatId: UUID) => void;
}

function ChatCard({ title, chatId, onDelete }: ChatCardProps) {
  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();

    if (!chatId) return;

    try {
      const response = await fetch(
        `${import.meta.env.VITE_BACKEND_URI}/delete_chat?chat_id=${chatId}`,
        { method: 'DELETE' }
      );

      if (response.ok && onDelete) {
        onDelete(chatId);
      }
    } catch (error) {
      console.error('Failed to delete chat:', error);
    }
  };

  return (
    <div className="chat-card">
      <h3>{title}</h3>
      {chatId && (
        <button
          className="delete-button"
          onClick={handleDelete}
          aria-label="Delete chat"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            width="16"
            height="16"
          >
            <path d="M3 6h18v2H3V6zm2 3h14v13a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V9zm5-6h4v2h-4V3z"/>
          </svg>
        </button>
      )}
    </div>
  );
}

export default ChatCard;
