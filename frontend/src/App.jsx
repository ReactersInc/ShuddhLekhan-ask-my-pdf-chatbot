// src/App.jsx
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import Dashboard from './pages/Dashboard';
import PDFviewerPage from './pages/PDFviewerPage';
import AuthPage from './pages/AuthPage';
import PlagiarismChecker from './pages/PlagiarismChecker';

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/auth" element={<AuthPage />}/>
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/pdf/:fileId" element={<PDFviewerPage />} />
      <Route path="/plagiarism-checker" element={<PlagiarismChecker />} />

      <Route path="*" element={<div>404 - Page Not Found</div>} />
    </Routes>
  );
};

export default App;
