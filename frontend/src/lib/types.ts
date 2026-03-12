// Types for LLM Agent Workspace System

export interface Agent {
  id: string
  name: string
  description: string
  status: 'idle' | 'executing' | 'completed' | 'failed'
  policy: Policy
  created_at: string
  updated_at: string
}

export interface Policy {
  id: string
  name: string
  constraints: string[]
  permissions: string[]
}

export interface ExecutionPlan {
  id: string
  agent_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  steps: PlanStep[]
  created_at: string
  completed_at?: string
}

export interface PlanStep {
  id: string
  order: number
  action: string
  description: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  result?: any
  error?: string
}

export interface Message {
  id: string
  conversation_id: string
  sender: 'user' | 'agent'
  content: string
  timestamp: string
}

export interface ToolCall {
  id: string
  name: string
  arguments: Record<string, unknown>
  result?: any
  timestamp: string
}

export interface WorkspaceFile {
  id: string
  path: string
  name: string
  type: 'file' | 'directory'
  content?: string
  metadata?: {
    size: number
    modified: string
  }
}

export interface ExecutionLog {
  id: string
  execution_id: string
  level: 'info' | 'warn' | 'error' | 'debug'
  message: string
  timestamp: string
  metadata?: Record<string, unknown>
}

export interface User {
  id: string
  username: string
  email: string
  role: 'admin' | 'user' | 'guest'
  created_at: string
}
