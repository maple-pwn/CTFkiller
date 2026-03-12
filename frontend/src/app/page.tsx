import Link from 'next/link'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <h1 className="text-4xl font-bold">LLM Agent Workspace</h1>
      <p className="mt-4 text-slate-300">Policy-Constrained LLM Agent Workspace System</p>
      <div className="mt-8 grid w-full max-w-xl grid-cols-1 gap-3 md:grid-cols-3">
        <Link href="/chat" className="rounded bg-blue-600 px-4 py-3 text-center font-medium text-white">
          Chat
        </Link>
        <Link href="/workspace" className="rounded bg-emerald-600 px-4 py-3 text-center font-medium text-white">
          Workspace
        </Link>
        <Link href="/execution-log" className="rounded bg-violet-600 px-4 py-3 text-center font-medium text-white">
          Timeline
        </Link>
      </div>
    </main>
  )
}
