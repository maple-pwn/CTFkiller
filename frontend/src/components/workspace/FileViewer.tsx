import { useMemo } from 'react';
import { FileNode, FileIcon } from './FileTree';

interface FileViewerProps {
  file: FileNode;
  onDownload?: () => void;
}

// Basic syntax highlighting for common languages
const getLanguageFromExtension = (name: string): string => {
  const parts = name.split('.');
  const ext = parts.length > 1 ? parts.pop()?.toLowerCase() || '' : '';
  
  const extensions: Record<string, string> = {
    tsx: 'typescript',
    ts: 'typescript',
    jsx: 'javascript',
    js: 'javascript',
    py: 'python',
    java: 'java',
    c: 'c',
    cpp: 'cpp',
    rs: 'rust',
    go: 'go',
    rb: 'ruby',
    php: 'php',
    sql: 'sql',
    md: 'markdown',
    txt: 'text',
    json: 'json',
    yaml: 'yaml',
    yml: 'yaml',
    xml: 'xml',
    html: 'html',
    css: 'css',
    scss: 'scss',
    sass: 'sass',
    less: 'less',
  };
  
  return extensions[ext] || 'text';
};

// Simple syntax highlighter
const SyntaxHighlighter = ({ code, language }: { code: string; language: string }) => {
  const highlight = (text: string, lang: string): string => {
    let highlighted = text;
    
    // HTML escape
    highlighted = highlighted
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
    
    // Common patterns for code files
    if (lang === 'javascript' || lang === 'typescript') {
      // Keywords
      highlighted = highlighted.replace(/\b(const|let|var|function|return|if|else|for|while|switch|case|break|continue|import|from|export|default|interface|type|class|extends|implements|new|this)\b/g, '<span class="text-purple-400">$1</span>');
      // Strings
      highlighted = highlighted.replace(/(['"`])(.*?)\1/g, '<span class="text-green-400">$1$2$1</span>');
      // Numbers
      highlighted = highlighted.replace(/\b(\d+)\b/g, '<span class="text-orange-400">$1</span>');
      // Functions
      highlighted = highlighted.replace(/(\w+)(?=\()/g, '<span class="text-blue-400">$1</span>');
      // Comments
      highlighted = highlighted.replace(/(\/\/.*|\/\*[\s\S]*?\*\/)/g, '<span class="text-gray-500 italic">$1</span>');
      // Booleans
      highlighted = highlighted.replace(/\b(true|false|null|undefined)\b/g, '<span class="text-red-400">$1</span>');
    }
    
    if (lang === 'python') {
      // Keywords
      highlighted = highlighted.replace(/\b(def|class|return|if|elif|else|for|while|break|continue|import|from|as|with|try|except|finally|raise|yield|lambda|pass|print|def)\b/g, '<span class="text-purple-400">$1</span>');
      // Strings
      highlighted = highlighted.replace(/(['"`])(.*?)\1/g, '<span class="text-green-400">$1$2$1</span>');
      // Numbers
      highlighted = highlighted.replace(/\b(\d+)\b/g, '<span class="text-orange-400">$1</span>');
      // Functions
      highlighted = highlighted.replace(/(\w+)(?=\()/g, '<span class="text-blue-400">$1</span>');
      // Comments
      highlighted = highlighted.replace(/(#.*)/g, '<span class="text-gray-500 italic">$1</span>');
      // Booleans
      highlighted = highlighted.replace(/\b(True|False|None)\b/g, '<span class="text-red-400">$1</span>');
    }
    
    if (lang === 'json') {
      // Keys
      highlighted = highlighted.replace(/(")(.*?)("):/g, '<span class="text-yellow-400">$1$2$3</span>:');
      // Strings
      highlighted = highlighted.replace(/"([^"]*)"/g, '<span class="text-green-400">"$1"</span>');
      // Numbers
      highlighted = highlighted.replace(/\b(\d+(\.\d+)?)\b/g, '<span class="text-orange-400">$1</span>');
      // Booleans
      highlighted = highlighted.replace(/\b(true|false|null)\b/g, '<span class="text-red-400">$1</span>');
    }
    
    if (lang === 'markdown') {
      // Headings
      highlighted = highlighted.replace(/^(#{1,6})\s+(.*)$/gm, '<span class="text-blue-400 font-bold">$1 $2</span>');
      // Bold
      highlighted = highlighted.replace(/\*\*(.*?)\*\*/g, '<span class="text-white font-bold">$1</span>');
      // Italic
      highlighted = highlighted.replace(/\*(.*?)\*/g, '<span class="text-gray-300 italic">$1</span>');
      // Code blocks
      highlighted = highlighted.replace(/`([^`]+)`/g, '<span class="text-orange-400 bg-orange-900/30 px-1 rounded">$1</span>');
      // Links
      highlighted = highlighted.replace(/\[(.*?)\]\((.*?)\)/g, '<span class="text-blue-400 underline">$1</span>');
    }
    
    if (lang === 'xml') {
      // Tags
      highlighted = highlighted.replace(/&lt;\/?(\w+)(.*?)&gt;/g, '&lt;/$1$2&gt;'.replace(/&lt;\/?(\w+)/g, '<span class="text-blue-400">&lt;$1</span>').replace(/(\w+)=(["\'])/g, '$1=$2'));
      // Attributes
      highlighted = highlighted.replace(/(\w+)="([^"]*)"/g, '<span class="text-purple-400">$1</span>="<span class="text-green-400">$2</span>"');
    }
    
    return highlighted;
  };

  return (
    <pre className="font-mono text-sm">
      <code dangerouslySetInnerHTML={{ __html: highlight(code, language) }} />
    </pre>
  );
};

// Format file size
const formatFileSize = (bytes?: number): string => {
  if (bytes === undefined) return 'Unknown';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
};

// Format date
const formatDate = (dateString?: string): string => {
  if (!dateString) return 'Unknown';
  try {
    return new Date(dateString).toLocaleString();
  } catch {
    return dateString;
  }
};

export function FileViewer({ file, onDownload }: FileViewerProps) {
  const language = useMemo(() => getLanguageFromExtension(file.name), [file.name]);
  
  const handleDownload = () => {
    if (onDownload) {
      onDownload();
    } else {
      // Default download behavior
      const element = document.createElement('a');
      const blob = new Blob([file.content || ''], { type: file.mimeType || 'text/plain' });
      element.href = URL.createObjectURL(blob);
      element.download = file.name;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    }
  };

  return (
    <div className="flex flex-col h-full w-full overflow-hidden bg-slate-900">
      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-700 bg-slate-800/50">
        <div className="flex items-center gap-3">
          <FileIcon type={file.type} name={file.name} />
          <div className="flex-1 min-w-0">
            <h2 className="text-sm font-medium text-gray-100 truncate">{file.name}</h2>
            <div className="flex items-center gap-4 text-xs text-gray-400">
              <span>Size: {formatFileSize(file.size)}</span>
              <span>Modified: {formatDate(file.modified)}</span>
              <span>Type: {file.mimeType || 'text/plain'}</span>
            </div>
          </div>
          <button
            onClick={handleDownload}
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4 bg-slate-900">
        {file.content === undefined ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <svg className="w-16 h-16 mb-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p>Select a file to view content</p>
          </div>
        ) : (
          <div className="relative group">
            <div className="absolute top-2 right-4 text-xs text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity">
              {language}
            </div>
            <SyntaxHighlighter code={file.content} language={language} />
          </div>
        )}
      </div>
    </div>
  );
}

export default FileViewer;
