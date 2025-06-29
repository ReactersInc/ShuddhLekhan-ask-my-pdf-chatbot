import React, { useState, useEffect } from "react";
import { Search, Upload, MessageSquare, Download, Trash2 } from 'lucide-react';
import './FileExplorer.css';

const FileExplorer = ({ selectedFolder, searchQuery, onSearchChange, onAIChatToggle }) => {
  const [files, setFiles] = useState([]);

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const res = await fetch("http://localhost:5000/documents/list");
        const data = await res.json();
        setFiles(data);
      } catch (err) {
        console.error("Failed to load files:", err);
      }
    };

    fetchFiles();
  }, []);

  const getFolderPath = (folderId) => {
    const folderMap = {
      '1-1': 'Research Papers / Machine Learning',
      '2-1': 'Legal Documents / Contracts',
      '3': 'Reports'
    };
    return folderMap[folderId] || 'All Files';
  };

  const filteredFiles = files.filter(
    (file) =>
      (!selectedFolder || file.folderId === selectedFolder) &&
      file.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="file-explore">

      <div className="file-header">
        <div>
          <h2>{getFolderPath(selectedFolder)}</h2>
          {selectedFolder && <small>{filteredFiles.length} files</small>}
        </div>

        <button className="ai-button" onClick={onAIChatToggle}>
          <MessageSquare size={16} />
          <span>AI Assistant</span>
        </button>
      </div>

      <div className="file-search">
        <Search size={16} />
        <input
          type="text"
          value={searchQuery}
          onChange={e => onSearchChange(e.target.value)}
          placeholder="Search for a Document or ask Ai for summaries ..."
        />
      </div>

      <div className="file-grid">
        {filteredFiles.length ? (
          filteredFiles.map(file => (
            <div
              key={file.id}
              className="file-card"
              onClick={() => window.open(`http://localhost:5000/uploads/${file.relative_path}`, '_blank')}
            >
              <div className="file-info">
                <div className="file-icon">PDF</div>
                <div>
                  <strong>{file.name}</strong>
                  <small>{file.size} • {file.uploadDate}</small>
                </div>
              </div>
              <div className="file-menu">
                <Download size={14} />
                <Trash2 size={14} />
              </div>
            </div>
          ))
        ) : (
          <div className="file-empty">
            <Upload size={48} />
            <p>No files found</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileExplorer;
