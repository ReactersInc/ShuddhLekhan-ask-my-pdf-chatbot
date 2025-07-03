import React, { useState, useRef, useEffect } from 'react';
import { FileText, Folder, Plus, Upload, Search, ChevronDown, ChevronRight } from 'lucide-react';
import './Sidebar.css';
import useFileUploader from '../../hooks/useFileUploader'
import { mergeFolderTrees } from '../../utils/mergeFolderTrees';
import { API_URL } from '../../config';



const FolderNode = ({ node, selectedFolder, onFolderSelect, toggleExpand, level = 0 }) => {
  return (
    <div style={{ marginLeft: `${level * 12}px` }}>
      <div
        className={`folder-item ${selectedFolder === node.id ? 'active' : ''}`}
        onClick={() => onFolderSelect(node.id)}
      >
        {node.children?.length > 0 && (
          <span
            className="chevron"
            onClick={e => {
              e.stopPropagation();
              toggleExpand(node.id);
            }}
          >
            {node.isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          </span>
        )}
        <Folder size={16} />
        <span>{node.name}</span>
        <span className="count">{node.count}</span>
      </div>

      {/* Recursively render children */}
      {node.isExpanded && node.children?.map(child => (
        <FolderNode
          key={child.id}
          node={child}
          selectedFolder={selectedFolder}
          onFolderSelect={onFolderSelect}
          toggleExpand={toggleExpand}
          level={level + 1} // indent deeper
        />
      ))}
    </div>
  );
};




const Sidebar = ({ selectedFolder, onFolderSelect, onUploadClick }) => {

  const [folders, setFolders] = useState([]);

  useEffect(() => {
    const fetchFolderTree = async () => {
      try {
        const res = await fetch(`${API_URL}/documents/tree`);
        const data = await res.json();
        console.log('fetchFolderTree', data);

        setFolders(data);
      } catch (err) {
        console.error("Failed to fetch folder tree", err);
      }
    };

    fetchFolderTree();
  }, []);




  const fileInputRef = useRef(null);
  const {
    uploading,
    uploadFiles,
    message
  } = useFileUploader();


  const toggleExpand = id => {
    setFolders(prev =>
      prev.map(f =>
        f.id === id ? { ...f, isExpanded: !f.isExpanded } : f
      )
    );
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      const uploadedTree = await uploadFiles(files);

      if (uploadedTree && uploadedTree.length > 0) {
        alert("Files uploaded and embedded successfully!");
        setFolders(prev => mergeFolderTrees(prev, uploadedTree));
      } else {
        alert("Upload failed or embedding did not complete.");
      }
    }

    e.target.value = ''; // reset file input
  };



  return (
    <div className="sidebar">
      <div className="sidebar-header">

        <h2 className="app-title">
          <FileText size={20} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
          ShudhLeekhan - <small>An AI Document Intelligence Platform</small>
        </h2>

        <button className="sidebar-button" onClick={handleUploadClick}>
          <Upload size={16} /> {uploading ? 'Uploading...' : 'Upload'}
        </button>

        <input
          type="file"
          accept=".pdf"
          multiple
          webkitdirectory="true"
          directory="true"
          ref={fileInputRef}
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />

        <button className="sidebar-button">
          <Plus size={16} /> New Folder
        </button>

        {message && (
          <p className={`upload-message ${message.toLowerCase().includes('success') ? 'success' : 'error'}`}>
            {message}
          </p>
        )}

      </div>

      <div className="folder-list">
        <div
          className={`folder-item ${!selectedFolder ? 'active' : ''}`}
          onClick={() => onFolderSelect(null)}
        >
          <Search size={16} />
          <span>All Files</span>
        </div>

        {folders.map(folder => (
          <FolderNode
            key={folder.id}
            node={folder}
            selectedFolder={selectedFolder}
            onFolderSelect={onFolderSelect}
            toggleExpand={toggleExpand}
          />
        ))}

      </div>
    </div>
  );
};

export default Sidebar;
