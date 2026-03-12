import { useState } from 'react';

// File/Folder type definitions
export interface FileNode {
  name: string;
  type: 'file' | 'folder';
  children?: FileNode[];
  size?: number;
  modified?: string;
  content?: string;
  mimeType?: string;
}

interface FileTreeProps {
  data: FileNode[];
  onFileSelect?: (file: FileNode) => void;
  selectedFile?: string;
  initialExpanded?: string[];
}

// Icon components for different file types
const FileIcon = ({ type, name }: { type: 'file' | 'folder'; name: string }) => {
  const getFileExtension = (name: string): string => {
    const parts = name.split('.');
    return parts.length > 1 ? parts.pop()?.toLowerCase() || '' : '';
  };

  const ext = getFileExtension(name);
  
  const icons: Record<string, string> = {
    tsx: 'text-purple-400',
    ts: 'text-blue-400',
    jsx: 'text-cyan-400',
    js: 'text-yellow-400',
    py: 'text-green-400',
    java: 'text-red-400',
    c: 'text-orange-400',
    cpp: 'text-orange-400',
    rs: 'text-purple-400',
    go: 'text-cyan-400',
    rb: 'text-red-400',
    php: 'text-blue-400',
    sql: 'text-yellow-400',
    md: 'text-gray-400',
    txt: 'text-gray-400',
    json: 'text-yellow-400',
    yaml: 'text-red-400',
    yml: 'text-red-400',
    xml: 'text-orange-400',
    html: 'text-red-400',
    css: 'text-blue-400',
    scss: 'text-red-400',
    png: 'text-green-400',
    jpg: 'text-green-400',
    jpeg: 'text-green-400',
    gif: 'text-green-400',
    svg: 'text-blue-400',
    ico: 'text-gray-400',
    dockerfile: 'text-blue-400',
    gitignore: 'text-red-400',
    env: 'text-yellow-400',
    pdf: 'text-red-400',
    zip: 'text-gray-400',
    rar: 'text-gray-400',
    tar: 'text-gray-400',
    gz: 'text-gray-400',
  };

  const iconClass = icons[ext] || 'text-gray-400';

  if (type === 'folder') {
    return (
      <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
      </svg>
    );
  }

  return (
    <svg className={`w-5 h-5 ${iconClass}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  );
};

const ExpandIcon = ({ expanded }: { expanded: boolean }) => (
  <svg
    className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${expanded ? 'rotate-180' : ''}`}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
  </svg>
);

interface FileTreeItemProps {
  node: FileNode;
  onFileSelect?: (file: FileNode) => void;
  selectedFile?: string;
  expandedNodes: Set<string>;
  toggleNode: (path: string) => void;
  depth?: number;
}

const FileTreeItem = ({ node, onFileSelect, selectedFile, expandedNodes, toggleNode, depth = 0 }: FileTreeItemProps) => {
  const isSelected = selectedFile === node.name;
  
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (node.type === 'folder') {
      toggleNode(node.name);
    } else {
      onFileSelect?.(node);
    }
  };

  const paddingLeft = `${depth * 16 + 12}px`;

  return (
    <div className="select-none">
      <div
        onClick={handleNodeClick}
        className={`flex items-center py-1 px-2 rounded cursor-pointer transition-colors duration-150 ${
          isSelected 
            ? 'bg-blue-500/20 text-blue-400' 
            : 'hover:bg-slate-700/50 text-gray-300'
        }`}
        style={{ paddingLeft }}
      >
        {node.type === 'folder' && (
          <div onClick={(e) => { e.stopPropagation(); toggleNode(node.name); }}>
            <ExpandIcon expanded={expandedNodes.has(node.name)} />
          </div>
        )}
        <span className="mr-2">
          <FileIcon type={node.type} name={node.name} />
        </span>
        <span className="truncate text-sm">{node.name}</span>
      </div>
      
      {node.type === 'folder' && expandedNodes.has(node.name) && node.children && (
        <div>
          {node.children.map((child) => (
            <FileTreeItem
              key={`${node.name}/${child.name}`}
              node={child}
              onFileSelect={onFileSelect}
              selectedFile={selectedFile}
              expandedNodes={expandedNodes}
              toggleNode={toggleNode}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export function FileTree({ data, onFileSelect, selectedFile, initialExpanded = [] }: FileTreeProps) {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set(initialExpanded));

  const toggleNode = (path: string) => {
    setExpandedNodes((prev) => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  };

  const expandAll = () => {
    const allFolders = new Set<string>();
    const traverse = (nodes: FileNode[]) => {
      for (const node of nodes) {
        if (node.type === 'folder') {
          allFolders.add(node.name);
          if (node.children) {
            traverse(node.children);
          }
        }
      }
    };
    traverse(data);
    setExpandedNodes(allFolders);
  };

  const collapseAll = () => {
    setExpandedNodes(new Set());
  };

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2 border-b border-slate-700 bg-slate-800/50">
        <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">Explorer</span>
        <div className="flex gap-2">
          <button
            onClick={expandAll}
            className="text-xs px-2 py-1 rounded hover:bg-slate-700 text-gray-400 transition-colors"
          >
            Expand All
          </button>
          <button
            onClick={collapseAll}
            className="text-xs px-2 py-1 rounded hover:bg-slate-700 text-gray-400 transition-colors"
          >
            Collapse All
          </button>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto py-2">
        {data.length === 0 ? (
          <div className="px-4 py-8 text-center text-gray-500 text-sm">
            No files found
          </div>
        ) : (
          data.map((node) => (
            <FileTreeItem
              key={node.name}
              node={node}
              onFileSelect={onFileSelect}
              selectedFile={selectedFile}
              expandedNodes={expandedNodes}
              toggleNode={toggleNode}
            />
          ))
        )}
      </div>
    </div>
  );
}

export default FileTree;

export { FileIcon };
