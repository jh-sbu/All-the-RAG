import { useState } from 'react';
import { IMessage } from '../Models/Message';
import './Chatbot.css';

function Chatbot() {
  const [messages, setMessages] = useState<IMessage[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = () => {
    if (!userInput.trim() || isLoading) return;

    // Create updated message array with new user message
    const newUserMessage: IMessage = { sender: 'user', text: userInput };
    const updatedMessages = [...messages, newUserMessage];

    // Update state immediately
    setMessages(updatedMessages);
    setUserInput('');
    setIsLoading(true);

    // Create assistant message entry immediately for streaming
    const assistantMessage: IMessage = { sender: 'assistant', text: '' };
    setMessages(prev => [...prev, assistantMessage]);

    // Stream response from backend
    fetch(`${import.meta.env.VITE_BACKEND_URI}/send_message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: updatedMessages.map(msg => ({
          role: msg.sender,
          content: msg.text
        }))
      }),
    })
      .then(async response => {
        if (!response.ok) throw new Error('Network response was not ok');

        const reader = response.body?.getReader();
        if (!reader) throw new Error('No response body');

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = new TextDecoder().decode(value);
          // Process each data line in the chunk
          const lines = chunk.split('\n');
          let contentAccumulator = '';

          lines.forEach(line => {
            if (line.startsWith('data: ')) {
              try {
                const json = JSON.parse(line.slice(6).trim());
                if (json.content) {
                  contentAccumulator += json.content;
                }
              } catch (e) {
                console.error('Error parsing JSON:', e);
              }
            }
          });

          if (contentAccumulator) {
            setMessages(prev => {
              const lastMessage = prev[prev.length - 1];
              if (lastMessage.sender === 'assistant') {
                return [
                  ...prev.slice(0, -1),
                  { ...lastMessage, text: lastMessage.text + contentAccumulator }
                ];
              }
              return prev;
            });
          }
        }
      })
      .catch(error => {
        console.error('Error:', error);
        setMessages(prev => {
          const lastMessage = prev[prev.length - 1];
          if (lastMessage.sender === 'assistant') {
            return [
              ...prev.slice(0, -1),
              { ...lastMessage, text: 'Sorry, there was an error processing your message' }
            ];
          }
          return prev;
        });
      })
      .finally(() => setIsLoading(false));
  };

  return (
    <div className="chatbot">
      <h2>All the RAG</h2>
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
          disabled={isLoading}
        />
        <button onClick={sendMessage} disabled={isLoading}>
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
}

export default Chatbot;
