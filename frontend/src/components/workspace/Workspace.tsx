'use client';

import { useState } from 'react';
import { FileTree, FileNode } from './FileTree';
import { FileViewer } from './FileViewer';

const mockFiles: FileNode[] = [
  {
    name: 'src',
    type: 'folder',
    children: [
      {
        name: 'components',
        type: 'folder',
        children: [
          { name: 'Header.tsx', type: 'file', size: 1234, modified: '2024-01-15T10:30:00', content: '// Header component', mimeType: 'text/typescript' },
          { name: 'Footer.tsx', type: 'file', size: 892, modified: '2024-01-14T09:20:00', content: '// Footer component', mimeType: 'text/typescript' },
        ],
      },
      {
        name: 'app',
        type: 'folder',
        children: [
          { name: 'layout.tsx', type: 'file', size: 567, modified: '2024-01-10T08:15:00', content: '// Layout', mimeType: 'text/typescript' },
          { name: 'page.tsx', type: 'file', size: 2345, modified: '2024-01-16T11:45:00', content: '// Page', mimeType: 'text/typescript' },
        ],
      },
    ],
  },
  {
    name: 'package.json',
    type: 'file',
    size: 1234,
    modified: '2024-01-05T14:00:00',
    content: '{ "name": "project", "version": "1.0.0" }',
    mimeType: 'application/json',
  },
  {
    name: 'README.md',
    type: 'file',
    size: 5678,
    modified: '2024-01-12T16:30:00',
    content: '# Project\n\nThis is a demo readme.',
    mimeType: 'text/markdown',
  },
];

export function Workspace() {
  const [selectedFile, setSelectedFile] = useState<FileNode | undefined>(undefined);

  return (
    <div className="flex h-full w-full bg-slate-900">
      <div className="w-64 flex-shrink-0 border-r border-slate-700">
        <FileTree
          data={mockFiles}
          selectedFile={selectedFile?.name}
          onFileSelect={setSelectedFile}
        />
      </div>

      <div className="flex-1 flex flex-col">
        {selectedFile ? (
          <FileViewer file={selectedFile} />
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            Select a file to view
          </div>
        )}
      </div>
    </div>
  );
}

export default Workspace;
