import React, { useState } from 'react';
import { FileText ,Folder, Plus, Upload, Search, ChevronDown, ChevronRight } from 'lucide-react';
import './Sidebar.css';

const Sidebar = ({ selectedFolder, onFolderSelect, onUploadClick }) => {
  const [folders, setFolders] = useState([
    {
      id: '1',
      name: 'Research Papers',
      count: 1,
      isExpanded: false,
      children: [
        { id: '1-1', name: 'Machine Learning', count: 1 },
        { id: '1-2', name: 'Data Science', count: 0 }
      ]
    },
    {
      id: '2',
      name: 'Legal Documents',
      count: 1,
      isExpanded: false,
      children: [
        { id: '2-1', name: 'Contracts', count: 1 },
        { id: '2-2', name: 'Policies', count: 0 }
      ]
    }
  ]);

  const toggleExpand = id => {
    setFolders(prev =>
      prev.map(f =>
        f.id === id ? { ...f, isExpanded: !f.isExpanded } : f
      )
    );
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2 className="app-title">
          <FileText size={20} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
          PDF AI
        </h2>
        <button className="sidebar-button" onClick={onUploadClick}>
          <Upload size={16} /> Upload
        </button>
        <button className="sidebar-button">
          <Plus size={16} /> New Folder
        </button>
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
