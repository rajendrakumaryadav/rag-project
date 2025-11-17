import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Message } from '../../api/client';
import { User, Bot, FileText, ExternalLink } from 'lucide-react';

interface MessageListProps {
  messages: Message[];
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  if (messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center max-w-md">
          <div className="mb-6">
            <div className="w-20 h-20 mx-auto bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg">
              <Bot className="h-10 w-10 text-white" />
            </div>
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-2">Welcome to AI Chat!</h3>
          <p className="text-gray-500">Start a conversation by typing a message below.</p>
          <p className="text-sm text-gray-400 mt-4">
            Ask me anything - I'm here to help! ✨
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {messages.map((message, index) => (
        <div
          key={message.id}
          className={`flex gap-4 ${
            message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
          } animate-fadeIn`}
          style={{ animationDelay: `${index * 0.05}s` }}
        >
          {/* Avatar */}
          <div
            className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center shadow-md ${
              message.role === 'user'
                ? 'bg-gradient-to-br from-indigo-600 to-purple-600'
                : 'bg-gradient-to-br from-gray-100 to-gray-200'
            }`}
          >
            {message.role === 'user' ? (
              <User className="h-5 w-5 text-white" />
            ) : (
              <Bot className="h-5 w-5 text-gray-700" />
            )}
          </div>

          {/* Message Content */}
          <div className={`flex-1 ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
            <div
              className={`inline-block max-w-full px-5 py-3 rounded-2xl shadow-md hover:shadow-lg transition-shadow duration-300 ${
                message.role === 'user'
                  ? 'bg-gradient-to-br from-indigo-600 to-purple-600 text-white'
                  : 'bg-white border border-gray-200 text-gray-900'
              }`}
            >
              {message.role === 'assistant' ? (
                <div className="prose prose-sm max-w-none prose-headings:mt-3 prose-headings:mb-2 prose-p:my-2 prose-ul:my-2 prose-ol:my-2 prose-li:my-0 prose-pre:my-2 prose-code:text-sm prose-a:text-indigo-600 prose-a:no-underline hover:prose-a:underline">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {message.content}
                  </ReactMarkdown>
                </div>
              ) : (
                <div className="whitespace-pre-wrap leading-relaxed">{message.content}</div>
              )}
            </div>

            {/* Source References */}
            {message.role === 'assistant' && message.sources && message.sources.length > 0 && (
              <div className="mt-3 space-y-2">
                <div className="text-xs font-semibold text-gray-600 flex items-center gap-1">
                  <FileText className="h-3 w-3" />
                  <span>Sources ({message.sources.length})</span>
                </div>
                <div className="space-y-1">
                  {message.sources.map((source: any, idx: number) => (
                    <div
                      key={idx}
                      className="flex items-start gap-2 p-2 bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-lg text-xs"
                    >
                      <ExternalLink className="h-3 w-3 text-emerald-600 flex-shrink-0 mt-0.5" />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-emerald-900 truncate">
                          {source.filename || source.source || `Source ${idx + 1}`}
                        </p>
                        {source.page && (
                          <p className="text-emerald-700">Page {source.page}</p>
                        )}
                        {source.content && (
                          <p className="text-emerald-800 mt-1 line-clamp-2">
                            {source.content}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div
              className={`text-xs mt-2 px-1 ${
                message.role === 'user' ? 'text-gray-500' : 'text-gray-500'
              }`}
            >
              {new Date(message.created_at).toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default MessageList;