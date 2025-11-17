import React from 'react';
import { Conversation } from '../../api/client';
import { Trash2, MessageSquare } from 'lucide-react';

interface ConversationListProps {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  onSelectConversation: (conversation: Conversation) => void;
  onDeleteConversation: (conversationId: number) => void;
}

const ConversationList: React.FC<ConversationListProps> = ({
  conversations,
  currentConversation,
  onSelectConversation,
  onDeleteConversation,
}) => {
  const handleDelete = (e: React.MouseEvent, conversationId: number) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      onDeleteConversation(conversationId);
    }
  };

  return (
    <div className="p-3">
      {conversations.length === 0 ? (
        <div className="text-center text-gray-500 py-12">
          <div className="mb-4">
            <div className="w-16 h-16 mx-auto bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center shadow-md">
              <MessageSquare className="h-8 w-8 text-gray-400" />
            </div>
          </div>
          <div className="text-sm font-medium text-gray-600">No conversations yet</div>
          <div className="text-xs mt-1 text-gray-400">Start a new chat to begin!</div>
        </div>
      ) : (
        conversations.map((conversation) => (
          <div
            key={conversation.id}
            onClick={() => onSelectConversation(conversation)}
            className={`group p-4 rounded-xl cursor-pointer mb-3 transition-all duration-300 relative ${
              currentConversation?.id === conversation.id
                ? 'bg-gradient-to-r from-indigo-50 to-purple-50 border-2 border-indigo-200 shadow-md'
                : 'hover:bg-gray-50 border-2 border-transparent hover:border-gray-200 hover:shadow-md'
            }`}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <div className="font-semibold text-gray-900 truncate mb-1">
                  {conversation.title}
                </div>
                <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
                  <span className="px-2 py-1 bg-indigo-100 text-indigo-700 rounded-md font-medium">
                    {conversation.provider}
                  </span>
                  <span className="text-gray-400">•</span>
                  <span>{conversation.model}</span>
                </div>
                <div className="text-xs text-gray-400 flex items-center gap-1">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                  </svg>
                  {new Date(conversation.updated_at).toLocaleDateString()}
                </div>
              </div>
              <button
                onClick={(e) => handleDelete(e, conversation.id)}
                className="opacity-0 group-hover:opacity-100 transition-all duration-300 p-2 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-600 transform hover:scale-110"
                title="Delete conversation"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
};

export default ConversationList;