import React from 'react';
import { Message } from './ChatInterface';

interface MessageListProps {
  messages: Message[];
  isSending: boolean;
  messagesEndRef: React.RefObject<HTMLDivElement>;
}

const MessageList: React.FC<MessageListProps> = ({ messages, isSending, messagesEndRef }) => {
  const getRoleClasses = (role: Message['role']) => {
    switch (role) {
      case 'user':
        return 'bg-blue-500 text-white';
      case 'assistant':
        return 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100';
      case 'system':
        return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200 border-l-4 border-yellow-500';
      default:
        return 'bg-gray-100 dark:bg-gray-700';
    }
  };

  const getRoleLabel = (role: Message['role']) => {
    switch (role) {
      case 'user':
        return 'You';
      case 'assistant':
        return 'Assistant';
      case 'system':
        return 'System';
      default:
        return 'Unknown';
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.length === 0 && (
        <div className="flex flex-col items-center justify-center h-full text-gray-500 dark:text-gray-400">
          <div className="mb-4 text-4xl">💬</div>
          <p className="text-lg">Start a conversation...</p>
        </div>
      )}

      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex w-full ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          role="article"
          aria-label={`${getRoleLabel(message.role)} message`}
        >
          <div
            className={`max-w-[85%] rounded-2xl px-4 py-3 shadow-sm ${
              message.role === 'user'
                ? 'rounded-tr-sm'
                : message.role === 'system'
                ? 'rounded-tl-sm w-full'
                : 'rounded-tl-sm'
            } ${getRoleClasses(message.role)}`}
          >
            <div className="flex items-baseline gap-2 mb-1">
              <span className="text-xs font-semibold opacity-80 uppercase">
                {getRoleLabel(message.role)}
              </span>
              <span className="text-xs opacity-60">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
            <div className="whitespace-pre-wrap text-sm leading-relaxed">
              {message.content}
            </div>
          </div>
        </div>
      ))}

      {isSending && (
        <div className="flex justify-start" aria-live="polite">
          <div className="max-w-[85%] rounded-2xl rounded-tl-sm bg-gray-100 dark:bg-gray-700 px-4 py-3">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;
