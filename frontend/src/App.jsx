// src/App.jsx
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import Dashboard from './pages/Dashboard';
import PDFviewerPage from './pages/PDFviewerPage';
import AuthPage from './pages/AuthPage';
import PlagiarismChecker from './pages/PlagiarismChecker';
import ProtectedRoute from './components/ProtectedRoute';

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/auth" element={<AuthPage />}/>
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      } />
      <Route path="/pdf/:fileId" element={
        <ProtectedRoute>
          <PDFviewerPage />
        </ProtectedRoute>
      } />
      <Route path="/plagiarism-checker" element={
        <ProtectedRoute>
          <PlagiarismChecker />
        </ProtectedRoute>
      } />

      <Route path="*" element={<div>404 - Page Not Found</div>} />
    </Routes>
  );
};

export default App;
