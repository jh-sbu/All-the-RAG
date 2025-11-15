import './NewChatButton.css';

interface NewChatButtonProps {
  onClick: () => void;
}

function NewChatButton({ onClick }: NewChatButtonProps) {
  return (
    <div className="new-chat-button" onClick={onClick}>
      <h3>New Chat</h3>
    </div>
  );
}

export default NewChatButton;
