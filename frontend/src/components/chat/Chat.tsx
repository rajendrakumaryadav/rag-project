import React, { useState, useEffect, useRef } from 'react';
import { Send, Plus, ChevronLeft, ChevronRight } from 'lucide-react';
import { chatAPI, configAPI, Conversation, Message, ChatResponse } from '../../api/client';
import ConversationList from './ConversationList';
import MessageList from './MessageList';
import ModelSelector from './ModelSelector';
import DocumentUpload from './DocumentUpload';

const Chat: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState('default');
  const [availableProviders, setAvailableProviders] = useState<any>({});
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversations and config on mount
  useEffect(() => {
    loadConversations();
    loadConfig();
  }, []);

  // Load messages when conversation changes
  useEffect(() => {
    if (currentConversation) {
      loadMessages(currentConversation.id);
    } else {
      setMessages([]);
    }
  }, [currentConversation]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadConversations = async () => {
    try {
      const convs = await chatAPI.listConversations();
      setConversations(convs);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const loadMessages = async (conversationId: number) => {
    try {
      const msgs = await chatAPI.getConversationMessages(conversationId);
      setMessages(msgs);
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  };

  const loadConfig = async () => {
    try {
      const config = await configAPI.getConfig();
      setAvailableProviders(config.providers || {});
    } catch (error) {
      console.error('Failed to load config:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;

    setLoading(true);
    try {
      const response: ChatResponse = await chatAPI.sendMessage({
        message: newMessage,
        provider: selectedProvider !== 'default' ? selectedProvider : undefined,
        conversation_id: currentConversation?.id,
      });

      // Update current conversation if new
      if (!currentConversation || currentConversation.id !== response.conversation_id) {
        await loadConversations();
        const newConv = conversations.find(c => c.id === response.conversation_id) ||
                       await chatAPI.listConversations().then(convs =>
                         convs.find(c => c.id === response.conversation_id)
                       );
        if (newConv) setCurrentConversation(newConv);
      }

      // Reload messages
      await loadMessages(response.conversation_id);
      
      // Update the last message with sources from the response
      if (response.sources && response.sources.length > 0) {
        setMessages(prevMessages => {
          const updatedMessages = [...prevMessages];
          const lastMessage = updatedMessages[updatedMessages.length - 1];
          if (lastMessage && lastMessage.role === 'assistant') {
            lastMessage.sources = response.sources;
          }
          return updatedMessages;
        });
      }

      setNewMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleNewConversation = () => {
    setCurrentConversation(null);
    setMessages([]);
  };

  const handleSelectConversation = (conversation: Conversation) => {
    setCurrentConversation(conversation);
  };

  const handleDeleteConversation = async (conversationId: number) => {
    try {
      await chatAPI.deleteConversation(conversationId);
      
      // If deleting current conversation, clear it
      if (currentConversation?.id === conversationId) {
        setCurrentConversation(null);
        setMessages([]);
      }
      
      // Reload conversations list
      await loadConversations();
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      alert('Failed to delete conversation. Please try again.');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(prev => !prev);
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
      {/* Sidebar - with collapse toggle */}
      <div className={`bg-white/80 backdrop-blur-xl border-r border-gray-200/50 flex flex-col shadow-xl transition-all duration-300 ${sidebarCollapsed ? 'w-16' : 'w-80'}`}>
        {/* Header */}
        <div className="p-4 border-b border-gray-200/50">
          {!sidebarCollapsed && (
            <>
              <div className="mb-4">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                  AI Chat
                </h1>
                <p className="text-xs text-gray-500 mt-1">Powered by Advanced AI</p>
              </div>
              <button
                onClick={handleNewConversation}
                className="w-full flex items-center justify-center px-4 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <Plus className="h-5 w-5 mr-2" />
                New Chat
              </button>
            </>
          )}
          {sidebarCollapsed && (
            <button
              onClick={handleNewConversation}
              className="w-full flex items-center justify-center p-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
              title="New Chat"
            >
              <Plus className="h-5 w-5" />
            </button>
          )}
        </div>

        {/* Toggle Button */}
        <div className="px-4 py-2 border-b border-gray-200/50">
          <button
            onClick={toggleSidebar}
            className="w-full flex items-center justify-center p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-all duration-300"
            title={sidebarCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          >
            {sidebarCollapsed ? <ChevronRight className="h-5 w-5" /> : <ChevronLeft className="h-5 w-5" />}
          </button>
        </div>

        {/* Conversations */}
        <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent">
          {!sidebarCollapsed && (
            <ConversationList
              conversations={conversations}
              currentConversation={currentConversation}
              onSelectConversation={handleSelectConversation}
              onDeleteConversation={handleDeleteConversation}
            />
          )}
          {sidebarCollapsed && (
            <div className="p-2">
              {conversations.slice(0, 10).map((conv) => (
                <button
                  key={conv.id}
                  onClick={() => handleSelectConversation(conv)}
                  className={`w-full p-2 mb-2 rounded-lg transition-all duration-300 ${
                    currentConversation?.id === conv.id
                      ? 'bg-gradient-to-r from-indigo-50 to-purple-50 border-2 border-indigo-200'
                      : 'hover:bg-gray-100 border-2 border-transparent'
                  }`}
                  title={conv.title}
                >
                  <div className="w-8 h-8 mx-auto rounded-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white flex items-center justify-center text-xs font-bold">
                    {conv.title.substring(0, 2).toUpperCase()}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Document Upload Section */}
        {!sidebarCollapsed && (
          <div className="p-4 border-t border-gray-200/50">
            <DocumentUpload onUploadComplete={loadConversations} />
          </div>
        )}
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        {/* Chat header */}
        <div className="bg-white/80 backdrop-blur-xl border-b border-gray-200/50 px-6 py-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                {currentConversation?.title || 'New Conversation'}
              </h2>
              {currentConversation && (
                <p className="text-sm text-gray-500 mt-1">
                  {currentConversation.provider} • {currentConversation.model}
                </p>
              )}
            </div>
            <ModelSelector
              selectedProvider={selectedProvider}
              availableProviders={availableProviders}
              onProviderChange={setSelectedProvider}
            />
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-6 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent">
          <MessageList messages={messages} />
          <div ref={messagesEndRef} />
        </div>

        {/* Message input */}
        <div className="bg-white/80 backdrop-blur-xl border-t border-gray-200/50 px-6 py-6 shadow-lg">
          <div className="max-w-4xl mx-auto">
            <div className="flex space-x-4 items-end">
              <div className="flex-1 relative">
                <textarea
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message... (Shift + Enter for new line)"
                  className="w-full resize-none rounded-2xl border-2 border-gray-200 px-6 py-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-300 shadow-sm hover:shadow-md bg-white"
                  rows={1}
                  disabled={loading}
                  style={{ minHeight: '56px', maxHeight: '200px' }}
                />
                {loading && (
                  <div className="absolute bottom-4 right-4">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-indigo-600"></div>
                  </div>
                )}
              </div>
              <button
                onClick={handleSendMessage}
                disabled={loading || !newMessage.trim()}
                className="inline-flex items-center justify-center p-4 border border-transparent font-medium rounded-2xl text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <Send className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;

