import React, { useState } from 'react';
import { sendMessage } from '../lib/api';
import ReactMarkdown from 'react-markdown';
import Image from 'next/image';

export default function ChatBot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendMessage(input);
      const assistantMessage = { 
        role: 'assistant', 
        content: Array.isArray(response.response) 
          ? response.response.map(msg => msg.content).join('\n') 
          : response.response,
        tools: response.tools 
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, something went wrong reaching the plant server. Please try again.',
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <h2 className="chat-title">Chat Interface</h2>
      <div className="messages-container">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role === 'user' ? 'message--user' : 'message--assistant'}`}>
            <div className={`message__bubble ${message.role === 'user' ? 'message__bubble--user' : 'message__bubble--assistant'}`}>
              {message.role === 'assistant' ? (
                <ReactMarkdown className="markdown-content">
                  {message.content}
                </ReactMarkdown>
              ) : (
                message.content
              )}
            </div>
            {message.tools && (
              <div className="message__tools">Tools: {message.tools.join(', ')}</div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="loading-indicator">
            <Image src="/assets/icons/view.gif" alt="Loading" width={24} height={24} />
            <span className="loading-text">Plantie Talkie is off to investigate...</span>
          </div>
        )}
      </div>
      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="input-field"
          placeholder="Ask about your plants..."
        />
        <button 
          onClick={handleSendMessage} 
          className="btn-primary"
          disabled={isLoading}
        >
          Send
        </button>
      </div>
    </div>
  );
}