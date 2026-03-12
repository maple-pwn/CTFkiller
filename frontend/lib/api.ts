const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Session {
  session_id: string;
  status: string;
  created_at: string;
}

export interface Message {
  id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}

export interface ExecutionLog {
  id: number;
  tool_name: string;
  arguments: string;
  result: string;
  status: string;
  error: string | null;
  started_at: string;
  completed_at: string | null;
}

export const api = {
  async createSession(): Promise<Session> {
    const res = await fetch(`${API_BASE_URL}/api/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) throw new Error('Failed to create session');
    return res.json();
  },

  async sendMessage(
    sessionId: string,
    content: string,
    agentType: 'default' | 'ctf_reverse' = 'default'
  ): Promise<{ success: boolean; response: string; violations?: string[] }> {
    const res = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, agent_type: agentType }),
    });
    if (!res.ok) throw new Error('Failed to send message');
    return res.json();
  },

  async getMessages(sessionId: string): Promise<Message[]> {
    const res = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/messages`);
    if (!res.ok) throw new Error('Failed to get messages');
    return res.json();
  },

  async getExecutionLogs(sessionId: string): Promise<ExecutionLog[]> {
    const res = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/logs`);
    if (!res.ok) throw new Error('Failed to get logs');
    return res.json();
  },
};
