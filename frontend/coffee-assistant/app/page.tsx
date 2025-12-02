'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Send, Coffee, Loader2, LogIn } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import LoginModal from '@/components/LoginModal';
import { chatAPI } from '@/lib/api';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

const exampleQueries = [
  "What drinkware products do you have?",
  "Show me coffee outlets near me",
  "What's the price range for tumblers?",
  "Are there any outlets in the city center?"
];

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage(inputMessage);
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.response || response.message || 'I received your message.',
        sender: 'assistant',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'assistant',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExampleClick = (query: string) => {
    setInputMessage(query);
  };

  const handleLoginSuccess = () => {
    router.push('/admin');
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-[#f5f7fa] to-[#e8ebf0]">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="bg-[#0E186C] p-2 rounded-xl">
              <Coffee className="text-white" size={28} />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-[#0E186C]">Coffee Assistant</h1>
              <p className="text-sm text-gray-600">AI-Powered Support</p>
            </div>
          </div>
          <button
            onClick={() => {
              if (isAuthenticated) {
                router.push('/admin');
              } else {
                setIsLoginModalOpen(true);
              }
            }}
            className="flex items-center space-x-2 bg-[#0E186C] text-white px-6 py-2.5 rounded-xl hover:bg-[#0a1150] transition-colors font-medium"
          >
            <LogIn size={20} />
            <span>{isAuthenticated ? 'Admin Dashboard' : 'Admin Login'}</span>
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden" style={{ height: 'calc(100vh - 200px)' }}>
          {/* Chat Area */}
          <div className="flex flex-col h-full">
            {/* Messages Container */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center">
                  <div className="bg-[#0E186C] bg-opacity-10 p-6 rounded-full mb-6">
                    <Coffee className="text-[#0E186C]" size={48} />
                  </div>
                  <h2 className="text-2xl font-bold text-[#0E186C] mb-3">
                    Welcome to Coffee Assistant
                  </h2>
                  <p className="text-gray-600 mb-8 max-w-md">
                    Ask me anything about our coffee outlets, drinkware products, or get recommendations!
                  </p>
                  
                  {/* Example Queries */}
                  <div className="w-full max-w-2xl">
                    <p className="text-sm font-medium text-gray-700 mb-3">Try these examples:</p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {exampleQueries.map((query, index) => (
                        <button
                          key={index}
                          onClick={() => handleExampleClick(query)}
                          className="text-left p-4 bg-gray-50 hover:bg-gray-100 rounded-xl transition-colors border border-gray-200 hover:border-[#0E186C]"
                        >
                          <p className="text-sm text-gray-700">{query}</p>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[70%] px-5 py-3 rounded-2xl ${
                          message.sender === 'user'
                            ? 'bg-[#0E186C] text-white'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
                        <p className={`text-xs mt-2 ${
                          message.sender === 'user' ? 'text-blue-200' : 'text-gray-500'
                        }`}>
                          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 px-5 py-3 rounded-2xl">
                        <Loader2 className="animate-spin text-[#0E186C]" size={20} />
                      </div>
                    </div>
                  )}
                </>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-gray-200 p-4 bg-gray-50">
              <form onSubmit={handleSendMessage} className="flex space-x-3">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Type your question here..."
                  className="flex-1 px-5 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#0E186C] focus:border-transparent transition-all"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={!inputMessage.trim() || isLoading}
                  className="bg-[#0E186C] text-white px-6 py-3 rounded-xl hover:bg-[#0a1150] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  <Send size={20} />
                  <span className="hidden sm:inline">Send</span>
                </button>
              </form>
            </div>
          </div>
        </div>
      </main>

      {/* Login Modal */}
      <LoginModal
        isOpen={isLoginModalOpen}
        onClose={() => setIsLoginModalOpen(false)}
        onSuccess={handleLoginSuccess}
      />
    </div>
  );
}
