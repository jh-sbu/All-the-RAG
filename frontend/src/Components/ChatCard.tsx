import { type MouseEvent, useState } from 'react';
import './ChatCard.css';
import { UUID } from '../Models/ChatSession';

interface ChatCardProps {
  title: string;
  chatId: UUID;
  onDelete: (chatId: UUID) => void;
  onClick: () => void;
}

function ChatCard({ title, chatId, onDelete, onClick }: ChatCardProps) {
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const openConfirm = (e: MouseEvent) => {
    e.stopPropagation();
    setIsConfirmOpen(true);
  };

  const closeConfirm = (e?: MouseEvent) => {
    e?.stopPropagation();
    if (isDeleting) return;
    setIsConfirmOpen(false);
  };

  const handleDelete = async () => {
    if (!chatId) return;

    try {
      setIsDeleting(true);
      const response = await fetch(
        `${import.meta.env.VITE_BACKEND_URI}/api/chat?chat_id=${chatId}`,
        { method: 'DELETE' }
      );

      if (response.ok && onDelete) {
        onDelete(chatId);
      }
    } catch (error) {
      console.error('Failed to delete chat:', error);
    } finally {
      setIsDeleting(false);
      setIsConfirmOpen(false);
    }
  };

  const handleCardClick = () => {
    onClick();
  };

  return (
    <>
      <div className="chat-card" onClick={handleCardClick}>
        <h3>{title}</h3>
        {chatId && (
          <button
            className="delete-button"
            onClick={openConfirm}
            aria-label="Delete chat"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="currentColor"
              width="16"
              height="16"
            >
              <path d="M3 6h18v2H3V6zm2 3h14v13a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V9zm5-6h4v2h-4V3z" />
            </svg>
          </button>
        )}
      </div>
      {isConfirmOpen && (
        <div className="delete-modal-overlay" onClick={closeConfirm}>
          <div className="delete-modal" onClick={(e) => e.stopPropagation()}>
            <p>
              Are you sure you want to delete "{title}"?
            </p>
            <div className="delete-modal__actions">
              <button
                type="button"
                className="delete-modal__cancel"
                onClick={closeConfirm}
                disabled={isDeleting}
              >
                Cancel
              </button>
              <button
                type="button"
                className="delete-modal__confirm"
                onClick={handleDelete}
                disabled={isDeleting}
              >
                {isDeleting ? 'Deleting…' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default ChatCard;
