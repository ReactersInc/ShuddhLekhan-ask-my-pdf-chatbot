import React, { useState } from 'react';
import Sidebar from '../components/Drive_view/Sidebar';
import FileExplorer from '../components/Drive_view/FileExplorer';
import AIChat from '../components/Drive_view/AIChat';
import UploadPDF from '../components/UploadPDF';
import './Dashboard.css';

const Dashboard = () => {
  const [selectedFolder, setSelectedFolder] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [selectedFileForChat, setSelectedFileForChat] = useState(null);

  return (
    <div className="dashboard">
      <Sidebar 
        selectedFolder={selectedFolder}
        onFolderSelect={setSelectedFolder}
        onUploadClick={() => setIsUploadModalOpen(true)}
      />

      <div className={`main-area ${isChatOpen ? 'shrinked' : ''}`}>
        <FileExplorer 
          selectedFolder={selectedFolder}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onAIChatToggle={() => setIsChatOpen(true)}
          onFileSelect={setSelectedFileForChat}
        />
      </div>

      {isChatOpen && (
        <AIChat 
          onClose={() => setIsChatOpen(false)} 
          selectedFile={selectedFileForChat} 

        />
      )}

      {isUploadModalOpen && (
        <div className="upload-modal-overlay" onClick={() => setIsUploadModalOpen(false)}>
          <div className="upload-modal" onClick={e => e.stopPropagation()}>
            <UploadPDF />
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
