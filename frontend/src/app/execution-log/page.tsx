"use client"

import Timeline from '@/components/execution/Timeline'
import type { ExecutionStep } from '@/components/execution/StepCard'

const demoSteps: ExecutionStep[] = [
  {
    id: '1',
    toolName: 'list_dir',
    args: { path: '/workspace/session' },
    result: { files: ['challenge.bin', 'notes.txt'] },
    status: 'completed',
    timestamp: new Date(),
    startTime: new Date(Date.now() - 4000),
    endTime: new Date(Date.now() - 3500),
  },
  {
    id: '2',
    toolName: 'strings',
    args: { file: 'challenge.bin' },
    status: 'running',
    timestamp: new Date(),
    startTime: new Date(Date.now() - 1000),
  },
]

export default function ExecutionLogPage() {
  return (
    <main className="min-h-screen p-4 md:p-6">
      <div className="mx-auto max-w-5xl">
        <h1 className="mb-4 text-xl font-semibold">Execution Timeline</h1>
        <Timeline steps={demoSteps} />
      </div>
    </main>
  )
}
