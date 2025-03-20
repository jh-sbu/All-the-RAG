import { useState } from 'react';
import { IMessage } from '../Models/Message';
import './Chatbot.css';

function Chatbot() {
  const [messages, setMessages] = useState<IMessage[]>([]);
  const [userInput, setUserInput] = useState('');

  const sendMessage = () => {
    if (!userInput.trim()) return;
    
    // Add user message immediately
    const newMessage: IMessage = { sender: 'user', text: userInput };
    setMessages(prev => [...prev, newMessage]);
    setUserInput('');

    // Send to backend
    fetch(`${import.meta.env.VITE_BACKEND_URI}/send_message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: userInput }),
    })
    .then(response => {
      if (!response.ok) throw new Error('Network response was not ok');
      return response.json();
    })
    .then(data => {
      // Add bot response from backend
      setMessages(prev => [...prev, { sender: 'bot', text: data.response }]);
    })
    .catch(error => {
      console.error('Error:', error);
      // Show error message to user
      setMessages(prev => [...prev, { 
        sender: 'bot', 
        text: 'Sorry, there was an error processing your message' 
      }]);
    });
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
          onKeyPress={e => e.key === 'Enter' && sendMessage()}
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default Chatbot;
