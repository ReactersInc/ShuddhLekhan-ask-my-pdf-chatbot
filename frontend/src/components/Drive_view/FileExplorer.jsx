import React, { useState } from "react";
import { Search, Upload, MessageSquare, Download, Trash2 } from 'lucide-react';
import './FileExplorer.css'

const FileExplorer = ({ selectedFolder, searchQuery, onSearchChange, onAIChatToggle }) => {

    const [files] = useState([
        { id: '1', name: 'Machine Learning Research.pdf', size: '2.4 MB', uploadDate: '2025-06-15', folderId: '1-1' },
        { id: '2', name: 'Contract Agreement.pdf', size: '1.8 MB', uploadDate: '2025-06-14', folderId: '2-1' },
        { id: '3', name: 'Annual Report 2023.pdf', size: '5.2 MB', uploadDate: '2025-06-13', folderId: '3' },
    ])


    // Geting folder hierarchy for breadcrumb navigation

    const getFolderPath = (folderId) => {
        const folderMap = {
            '1-1': 'Research Papers / Machine Learning',
            '2-1': 'Legal Documents / Contracts',
            '3': 'Reports'
        };
        return folderMap[folderId] || 'All Files';
    };

    const filteredFiles = files.filter(file => (!selectedFolder || file.folderId === selectedFolder) && file.name.toLowerCase().includes(searchQuery.toLowerCase()))

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
                <input type="text"
                    value={searchQuery}
                    onChange={e => onSearchChange(e.target.value)}
                    placeholder="Search for a Document or ask Ai for summaries ..."
                />
            </div>

            <div className="file-grid">
                {filteredFiles.length ? (
                    filteredFiles.map(file => (
                        <div key={file.id} className="file-card">
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

    )

}

export default FileExplorer