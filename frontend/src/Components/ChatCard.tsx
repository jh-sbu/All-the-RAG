import './ChatCard.css';

interface ChatCardProps {
  title: string;
}

function ChatCard({ title }: ChatCardProps) {
  return (
    <div className="chat-card">
      <h3>{title}</h3>
    </div>
  );
}

export default ChatCard;
