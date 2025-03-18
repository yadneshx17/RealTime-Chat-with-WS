import React, { useState, useEffect, useRef } from 'react';
import Login from './components/Login';
import Register from './components/Register';
import './App.css';

interface Message {
  content: string;
  sender: string;
  timestamp: string;
  isSent: boolean;
}

type AuthView = 'login' | 'register' | 'chat';

function App() {
  const [authView, setAuthView] = useState<AuthView>('login');
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [clientId] = useState(Math.floor(Math.random() * 10000));
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (authView === 'chat') {
      const ws = new WebSocket(`ws://localhost:8000/ws/${clientId}`);

      ws.onopen = () => {
        console.log('Connected to WebSocket');
      };

      ws.onmessage = (event) => {
        const message = event.data;
        if (!message.includes(`User ${clientId}`)) {
          setMessages((prev: Message[]) => [
            ...prev,
            {
              content: message,
              sender: message.split(':')[0],
              timestamp: new Date().toLocaleTimeString(),
              isSent: false
            },
          ]);
        }
      };

      ws.onclose = () => {
        console.log('Disconnected from WebSocket');
      };

      wsRef.current = ws;

      return () => {
        ws.close();
      };
    }
  }, [clientId, authView]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (newMessage.trim() && wsRef.current?.readyState === WebSocket.OPEN) {
      const messageToSend = `User ${clientId}: ${newMessage}`;
      wsRef.current.send(messageToSend);
      setMessages(prev => [
        ...prev,
        {
          content: newMessage,
          sender: `You (${clientId})`,
          timestamp: new Date().toLocaleTimeString(),
          isSent: true
        }
      ]);
      setNewMessage('');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    if (wsRef.current) {
      wsRef.current.close();
    }
    setAuthView('login');
    setMessages([]);
    setNewMessage('');
  };

  const renderContent = () => {
    switch (authView) {
      case 'login':
        return (
          <Login
            onLoginSuccess={() => setAuthView('chat')}
            onSwitchToRegister={() => setAuthView('register')}
          />
        );
      case 'register':
        return (
          <Register
            onRegisterSuccess={() => setAuthView('login')}
            onSwitchToLogin={() => setAuthView('login')}
          />
        );
      case 'chat':
        return (
          <div className="app">
            <div className="chat-container">
              <div className="chat-header">
                <h1>Real-time Chat</h1>
                <div className="header-right">
                  <p>Your ID: {clientId}</p>
                  <button onClick={handleLogout} className="logout-button">
                    Logout
                  </button>
                </div>
              </div>
              
              <div className="messages">
                {messages.map((message: Message, index: number) => (
                  <div key={index} className="message">
                    <div className="message-sender">{message.sender}</div>
                    <div className="message-content">{message.content}</div>
                    <div className="message-time">{message.timestamp}</div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>

              <form onSubmit={handleSendMessage} className="message-form">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Type a message..."
                />
                <button type="submit">Send</button>
              </form>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return renderContent();
}

export default App; 