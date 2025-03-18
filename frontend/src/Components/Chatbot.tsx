import { useState } from 'react';
import { IMessage } from '../Models/Message';
import './Chatbot.css';

function Chatbot() {
  const [messages, setMessages] = useState<IMessage[]>([]);
  const [userInput, setUserInput] = useState('');

  const sendMessage = () => {
    if (!userInput.trim()) return;
    const newMessage: IMessage = { sender: 'user', text: userInput };
    setMessages([...messages, newMessage]);
    setUserInput('');
    // simulate bot response
    setTimeout(() => {
      setMessages(prev => [...prev, { sender: 'bot', text: `You said: ${newMessage.text}` }]);
    }, 500);
  };

  return (
    <div className="chatbot">
      <h2>Chatbot</h2>
      <div className="chat-window">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            <strong>{msg.sender}:</strong> {msg.text}
          </div>
        ))}
      </div>
      <div className="chat-input">
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default Chatbot;
