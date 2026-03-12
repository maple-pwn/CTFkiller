"use client";

import React, { useState, useRef, useEffect } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [agentType, setAgentType] = useState<'default' | 'ctf_reverse'>('default');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const ensureSession = async (): Promise<string> => {
    if (sessionId) return sessionId;

    const res = await fetch(`${apiBase}/api/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) {
      throw new Error('Failed to create session');
    }
    const data = await res.json();
    setSessionId(data.session_id);
    return data.session_id;
  };

  const sendMessage = async (content: string) => {
    if (!content.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newMessage]);
    setIsSending(true);

    try {
      const activeSessionId = await ensureSession();
      const res = await fetch(`${apiBase}/api/sessions/${activeSessionId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: content.trim(), agent_type: agentType }),
      });

      if (!res.ok) {
        throw new Error('Failed to send message');
      }

      const data = await res.json();
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || 'No response received.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'system',
        content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto bg-white dark:bg-gray-900 rounded-lg shadow-lg overflow-hidden">
      <div className="border-b border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-800">
        <label className="mr-2 text-sm font-medium text-gray-700 dark:text-gray-200" htmlFor="agent-type">
          Agent
        </label>
        <select
          id="agent-type"
          className="rounded-md border border-gray-300 bg-white px-2 py-1 text-sm text-gray-900 dark:border-gray-600 dark:bg-gray-900 dark:text-gray-100"
          value={agentType}
          onChange={(e) => setAgentType(e.target.value as 'default' | 'ctf_reverse')}
          disabled={isSending}
        >
          <option value="default">default</option>
          <option value="ctf_reverse">ctf_reverse</option>
        </select>
      </div>
      <MessageList
        messages={messages}
        isSending={isSending}
        messagesEndRef={messagesEndRef}
      />
      <MessageInput
        onSend={sendMessage}
        isDisabled={isSending}
        placeholder="Type a message..."
      />
    </div>
  );
};

export default ChatInterface;
