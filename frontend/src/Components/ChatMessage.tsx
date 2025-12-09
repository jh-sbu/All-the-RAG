import { IMessage } from '../Models/Message';
import './ChatMessage.css';

interface ChatMessageProps {
  message: IMessage;
}

function ChatMessage({ message }: ChatMessageProps) {
  return (
    <div className={`chat-message ${message.sender}`}>
      <strong>{message.sender}:</strong> {message.text}
    </div>
  );
}

export default ChatMessage;
