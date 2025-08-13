import React, { useState } from 'react';
import { Upload, Download, FileText, CheckCircle, AlertCircle, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './PlagiarismChecker.css';

const PlagiarismChecker = () => {
  const navigate = useNavigate();
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [report, setReport] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFileUpload = (file) => {
    if (file.type === 'application/pdf') {
      setUploadedFile(file);
      setReport(null);
    } else {
      alert('Please upload a PDF file only.');
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

const startPlagiarismCheck = async () => {
  if (!uploadedFile) return;

  setIsProcessing(true);
  setProgress(0);

  // Simulate progress bar until backend responds
  const interval = setInterval(() => {
    setProgress(prev => {
      if (prev >= 95) {
        clearInterval(interval);
        return 95;
      }
      return prev + Math.random() * 15;
    });
  }, 200);

  try {
    const formData = new FormData();
    formData.append("file", uploadedFile);

    const res = await fetch("http://localhost:5000/plagiarism/upload", {
      method: "POST",
      body: formData
    });

    if (!res.ok) throw new Error(`Server error: ${res.status}`);
    const data = await res.json();

    // Assuming backend returns:
    // { overallSimilarity: number, sources: number, downloadUrl: string }
    const reportData = {
      id: `report_${Date.now()}`,
      fileName: uploadedFile.name,
      overallSimilarity: data.overallSimilarity, 
      sources: data.sources,
      generatedAt: new Date().toISOString(),
      downloadUrl: data.downloadUrl || '#'
    };

    setProgress(100);
    setTimeout(() => {
      setReport(reportData);
      setIsProcessing(false);
    }, 500);

  } catch (err) {
    console.error(err);
    setIsProcessing(false);
    alert("Error uploading or processing file.");
  }
};


  const handleDownloadReport = () => {
    if (report) {
      alert(`Downloading report for ${report.fileName}`);
    }
  };

  const resetChecker = () => {
    setUploadedFile(null);
    setReport(null);
    setIsProcessing(false);
    setProgress(0);
  };

  return (
    <div className="pc-container">
      <div className="pc-header">
        <button className="pc-btn pc-btn-ghost" onClick={() => navigate('/')}>
          <ArrowLeft size={16} /> Back to Files
        </button>
        <div>
          <h1>Plagiarism Checker</h1>
          <p>Upload a PDF to check for plagiarism and similarity</p>
        </div>
      </div>

      {/* Upload */}
      {!uploadedFile && !isProcessing && !report && (
        <div className="pc-card">
          <h2>Upload Document</h2>
          <p className="pc-desc">Upload a PDF file to check for plagiarism. Max: 10MB</p>
          <div
            className={`pc-dropzone ${dragActive ? 'active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <Upload size={48} className="pc-icon" />
            <p>Drag and drop your PDF here, or</p>
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => e.target.files && handleFileUpload(e.target.files[0])}
              id="file-upload"
              style={{ display: 'none' }}
            />
            <label htmlFor="file-upload" className="pc-btn pc-btn-outline">Choose File</label>
          </div>
        </div>
      )}

      {/* File Selected */}
      {uploadedFile && !isProcessing && !report && (
        <div className="pc-card">
          <h2>File Ready for Analysis</h2>
          <div className="pc-file-info">
            <FileText size={32} className="pc-icon-red" />
            <div>
              <p className="pc-filename">{uploadedFile.name}</p>
              <p className="pc-filesize">{(uploadedFile.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
            <button className="pc-btn pc-btn-outline" onClick={resetChecker}>Remove</button>
          </div>
          <button className="pc-btn" onClick={startPlagiarismCheck}>Start Plagiarism Check</button>
        </div>
      )}

      {/* Processing */}
      {isProcessing && (
        <div className="pc-card">
          <h2>Analyzing Document</h2>
          <p className="pc-desc">Please wait while we check your document...</p>
          <div className="pc-progress">
            <div className="pc-progress-bar" style={{ width: `${progress}%` }}></div>
          </div>
          <p className="pc-progress-text">{Math.round(progress)}%</p>
        </div>
      )}

      {/* Report */}
      {report && (
        <>
          <div className="pc-card">
            <h2><CheckCircle className="pc-icon-green" /> Analysis Complete</h2>
            <p className="pc-desc">Plagiarism check completed for {report.fileName}</p>
            <div className="pc-report-stats">
              <div className="pc-stat">
                <span className="pc-stat-value pc-blue">{report.overallSimilarity}%</span>
                <span>Overall Similarity</span>
              </div>
              <div className="pc-stat">
                <span className="pc-stat-value pc-purple">{report.sources}</span>
                <span>Sources Found</span>
              </div>
              <div className="pc-stat">
                <span className="pc-stat-value pc-green">{100 - report.overallSimilarity}%</span>
                <span>Original Content</span>
              </div>
            </div>
            <div className="pc-btn-group">
              <button className="pc-btn" onClick={handleDownloadReport}>
                <Download size={16} /> Download Full Report
              </button>
              <button className="pc-btn pc-btn-outline" onClick={resetChecker}>Check Another Document</button>
            </div>
          </div>

          {report.overallSimilarity > 25 && (
            <div className="pc-card pc-alert">
              <AlertCircle className="pc-icon-orange" />
              <div>
                <p className="pc-alert-title">High Similarity Detected</p>
                <p>This document has {report.overallSimilarity}% similarity with existing sources.</p>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default PlagiarismChecker;
