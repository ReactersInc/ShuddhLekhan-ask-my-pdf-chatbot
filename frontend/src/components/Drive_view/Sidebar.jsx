import React, { useState, useRef , useEffect} from 'react';
import { FileText, Folder, Plus, Upload, Search, ChevronDown, ChevronRight } from 'lucide-react';
import './Sidebar.css';
import useFileUploader from '../../hooks/useFileUploader'
import { mergeFolderTrees } from '../../utils/mergeFolderTrees';
import { API_URL } from '../../config';


const Sidebar = ({ selectedFolder, onFolderSelect, onUploadClick }) => {

  const [folders, setFolders] = useState([]);

  useEffect(() => {
    const fetchFolderTree = async () => {
      try {
        const res = await fetch(`${API_URL}/documents/tree`);
        const data = await res.json();
        console.log('fetchFolderTree',data);
        
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
      setFolders(prev => mergeFolderTrees(prev, uploadedTree));
    }
    e.target.value = ''; // reset input
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
          <div key={folder.id}>
            <div
              className={`folder-item ${selectedFolder === folder.id ? 'active' : ''}`}
              onClick={() => onFolderSelect(folder.id)}
            >
              {folder.children?.length > 0 && (
                <span
                  className="chevron"
                  onClick={e => {
                    e.stopPropagation();
                    toggleExpand(folder.id);
                  }}
                >
                  {folder.isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                </span>
              )}
              <Folder size={16} />
              <span>{folder.name}</span>
              <span className="count">{folder.count}</span>
            </div>

            {folder.isExpanded &&
              folder.children?.map(child => (
                <div
                  key={child.id}
                  className={`folder-sub ${selectedFolder === child.id ? 'active' : ''}`}
                  onClick={() => onFolderSelect(child.id)}
                >
                  <Folder size={14} />
                  <span>{child.name}</span>
                  <span className="count">{child.count}</span>
                </div>
              ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Sidebar;
