import { useState } from 'react';

function Chatbot() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState('');

  const sendMessage = () => {
    if (!userInput.trim()) return;
    const newMessage: Message = { sender: 'user', text: userInput };
    setMessages([...messages, newMessage]);
    setUserInput('');
    // simulate bot response
    setTimeout(() => {
      setMessages(prev => [...prev, { sender: 'bot', text: `You said: ${newMessage.text}` }]);
    }, 500);
  };

  return (
    <div className="chatbot" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
      <h2>Chatbot</h2>
      <div
        className="chat-window"
        style={{ border: '1px solid #ccc', padding: '10px', flex: 1, marginBottom: '10px', overflowY: 'auto' }}
      >
        {messages.map((msg, index) => (
          <div key={index} style={{ textAlign: msg.sender === 'bot' ? 'left' : 'right' }}>
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
