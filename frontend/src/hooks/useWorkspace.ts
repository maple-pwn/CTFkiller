// Placeholder hook for workspace management
import { useState, useCallback } from 'react'
import type { WorkspaceFile } from '@/lib/types'

export function useWorkspace() {
  const [files, setFiles] = useState<WorkspaceFile[]>([])
  const [selectedFile, setSelectedFile] = useState<WorkspaceFile | null>(null)

  const loadFiles = useCallback(async () => {
    // Implementation in Wave 2
  }, [])

  return {
    files,
    selectedFile,
    setSelectedFile,
    loadFiles,
  }
}
