import { useState } from 'react';
import { IMessage } from '../Models/Message';
import { ISource } from '../Models/Source';
import './Chatbot.css';
import { UUID } from '../Models/ChatSession';
import { Session } from '@supabase/supabase-js';
import { apiFetch } from '../lib/api';

interface ChatbotProps {
  messages: IMessage[];
  setMessages: React.Dispatch<React.SetStateAction<IMessage[]>>;
  chatId: UUID | "None";
  setChatId: React.Dispatch<React.SetStateAction<UUID | "None">>;
  onUpdateSources: (sources: ISource[]) => void;
  onRefreshChats: () => Promise<void>;
  session: Session | null;
}

function Chatbot({ messages, setMessages, chatId, setChatId, onUpdateSources, onRefreshChats, session }: ChatbotProps) {
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [healthStatus, setHealthStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const checkHealth = async () => {
    try {
      const response = await apiFetch('/health_check', {
        method: 'GET',
      });

      if (response.ok) {
        setHealthStatus('success');
      } else {
        setHealthStatus('error');
      }
    } catch (error) {
      console.error('Health check failed:', error);
      setHealthStatus('error');
    }

    // Reset status after 2 seconds
    setTimeout(() => setHealthStatus('idle'), 2000);
  };

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
    apiFetch('/api/message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: updatedMessages.map(msg => ({
          role: msg.sender,
          content: msg.text
        })),
        uuid: chatId
      }),
    })
      .then(async response => {
        if (!response.ok) throw new Error('Network response was not ok');

        const reader = response.body?.getReader();
        if (!reader) throw new Error('No response body');

        let buffer = '';
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += new TextDecoder().decode(value);
          // console.log(`Buffer: ${buffer}`);
          const lines = buffer.split('\n');

          // Keep the last incomplete line in the buffer
          buffer = lines.pop() || '';

          let currentEvent = '';
          let currentData = '';

          for (const line of lines) {
            if (line.startsWith('event: ')) {
              currentEvent = line.slice(7).trim();
            } else if (line.startsWith('data: ')) {
              currentData = line.slice(6).trim();
            } else if (line === '' && currentEvent && currentData) {
              // End of SSE message, process it
              try {
                const json = JSON.parse(currentData);

                if (currentEvent === 'new_chunk') {
                  if (json.content) {
                    setMessages(prev => {
                      const lastMessage = prev[prev.length - 1];
                      if (lastMessage.sender === 'assistant') {
                        return [
                          ...prev.slice(0, -1),
                          { ...lastMessage, text: lastMessage.text + json.content }
                        ];
                      }
                      return prev;
                    });
                  }
                } else if (currentEvent === 'update_sources') {
                  // console.log(`Got a source update: ${currentData}`);
                  if (json.sources && Array.isArray(json.sources)) {
                    const newSources: ISource[] = json.sources.map((source: any, index: number) => ({
                      number: index + 1,
                      title: source.title || '',
                      summary: source.summary || '',
                      url: source.url || ''
                    }));
                    onUpdateSources(newSources);
                  }
                } else if (currentEvent === 'set_uuid') {
                  if (json.new_uuid) {
                    setChatId(json.new_uuid);
                  }
                }
              } catch (e) {
                console.error('Error parsing SSE data:', e);
              }

              // Reset for next event
              currentEvent = '';
              currentData = '';
            }
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
      .finally(() => {
        setIsLoading(false);
        // TODO - this is extraneous after the first message of a new chat, fix this
        onRefreshChats();
      });
  };

  return (
    <div className="chatbot">
      <div className="header">
        <h2>Chat</h2>
        <button
          className={`health-check-btn ${healthStatus}`}
          onClick={checkHealth}
        >
          {healthStatus === 'idle' && 'Test'}
          {healthStatus === 'success' && '✓ Success'}
          {healthStatus === 'error' && '✗ Error'}
        </button>
      </div>
      {!session && messages.length === 0 && (
        <div className="auth-notice">
          <p>You can use the chatbot without logging in, but your conversation history won't be saved.</p>
          <p>Log in to save your chats and access them later.</p>
        </div>
      )}
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
