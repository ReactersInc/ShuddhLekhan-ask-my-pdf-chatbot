import React, { useState, useRef, useEffect } from 'react';
import { FileText, Folder, Plus, Upload, Search, ChevronDown, ChevronRight, Shield, Trash2 } from 'lucide-react';
import './Sidebar.css';
import useFileUploader from '../../hooks/useFileUploader';
import { mergeFolderTrees } from '../../utils/mergeFolderTrees';
import { API_URL } from '../../config/config';
import { useNavigate } from 'react-router-dom';
import UserProfile from '../UserProfile';
import { authFetchJson, authFetch } from '../../utils/authFetch';

const FolderNode = ({ node, selectedFolder, onFolderSelect, toggleExpand, onDeleteFolder, level = 0 }) => {
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
        <Trash2 
          size={14} 
          style={{ marginLeft: 'auto', cursor: 'pointer', color: '#888' }}
          onClick={(e) => {
            e.stopPropagation();
            onDeleteFolder(node.name);
          }}
        />
      </div>

      {/* Recursively render children */}
      {node.isExpanded && node.children?.map(child => (
        <FolderNode
          key={child.id}
          node={child}
          selectedFolder={selectedFolder}
          onFolderSelect={onFolderSelect}
          toggleExpand={toggleExpand}
          onDeleteFolder={onDeleteFolder}
          level={level + 1}
        />
      ))}
    </div>
  );
};

const Sidebar = ({ selectedFolder, onFolderSelect }) => {
  const navigate = useNavigate();
  const [folders, setFolders] = useState([]);

  useEffect(() => {
    const fetchFolderTree = async () => {
      try {
        const data = await authFetchJson('/documents/tree');
        // Backend returns array with folders and files
        if (Array.isArray(data)) {
          // Extract only folders for sidebar navigation
          const folderItems = data.filter(item => item.type === 'folder');
          setFolders(folderItems);
        } else {
          console.warn('Unexpected tree format:', data);
          setFolders([]);
        }
      } catch (err) {
        console.error("Failed to fetch folder tree", err);
        setFolders([]);
      }
    };
    fetchFolderTree();
  }, []);

  const fileInputRef = useRef(null);
  const { uploading, uploadFiles, message } = useFileUploader();

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

  const handleDeleteFolder = async (folderName) => {
    if (!confirm(`Are you sure you want to delete the folder "${folderName}" and all its files?`)) {
      return;
    }

    try {
      const response = await authFetch('/documents/folder', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          folder_name: folderName
        })
      });

      if (!response.ok) {
        throw new Error('Failed to delete folder');
      }

      const result = await response.json();
      // Refresh folder list
      setFolders(folders.filter(f => f.name !== folderName));
      
      // If the deleted folder was selected, clear selection
      if (selectedFolder === folderName || selectedFolder === `folder_${folderName}`) {
        onFolderSelect(null);
      }
      
      alert(`Folder deleted successfully. ${result.files_deleted} files removed.`);
    } catch (err) {
      console.error('Error deleting folder:', err);
      alert(`Failed to delete folder: ${err.message}`);
    }
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2 className="app-title">
          <FileText size={20} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
          ShudhLeekhan - <small>An AI Document Intelligence Platform</small>
        </h2>

        {/* Upload Button */}
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

        {/* New Folder Button */}
        <button className="sidebar-button">
          <Plus size={16} /> New Folder
        </button>

        {/* Plagiarism Check Button */}
        <button
          className="sidebar-button"
          onClick={() => navigate('/plagiarism-checker')}
        >
          <Shield size={16} /> Plagiarism Check
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
          onClick={() => {
            console.log('All Files clicked');
            onFolderSelect(null);
          }}
        >
          <Search size={16} />
          <span>All Files</span>
        </div>

        {Array.isArray(folders) && folders.map(folder => (
          <div
            key={folder.id || folder.name}
            className={`folder-item ${selectedFolder === folder.name ? 'active' : ''}`}
            onClick={() => {
              console.log('Folder clicked:', folder.name);
              onFolderSelect(folder.name);
            }}
          >
            <Folder size={16} />
            <span>{folder.name}</span>
            <span className="count">{folder.count || folder.children?.length || 0}</span>
            <Trash2 
              size={14} 
              style={{ marginLeft: 'auto', cursor: 'pointer', color: '#888' }}
              onClick={(e) => {
                e.stopPropagation();
                handleDeleteFolder(folder.name);
              }}
            />
          </div>
        ))}
      </div>

      {/* User Profile Component */}
      <UserProfile />
    </div>
  );
};

export default Sidebar;
