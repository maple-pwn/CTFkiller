// Placeholder hook for chat interactions
import { useState, useCallback } from 'react'
import type { Message } from '@/lib/types'

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isSending, setIsSending] = useState(false)

  const sendMessage = useCallback(async (content: string) => {
    setIsSending(true)
    // Implementation in Wave 2
    setIsSending(false)
  }, [])

  return {
    messages,
    isSending,
    sendMessage,
  }
}
