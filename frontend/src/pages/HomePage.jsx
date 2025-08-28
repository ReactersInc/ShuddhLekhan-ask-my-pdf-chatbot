// src/pages/HomePage.jsx
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import UploadPDF from '../components/UploadPDF';
import PDFList from '../components/PDFList';
// import AskQuestion from '../components/AskQuestion';

const HomePage = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // If user is already logged in, redirect to dashboard
    const token = localStorage.getItem('token');
    if (token) {
      navigate('/dashboard');
    }
  }, [navigate]);

  return (
    <div>
      <h1>AI PDF Summarizer Chatbot</h1>
      <p>Please <a href="/auth">login</a> to access your documents</p>
      <section>
        <UploadPDF />
      </section>
      <section>
        <PDFList />
      </section>
      {/* <section>
        <AskQuestion />
      </section> */}
    </div>
  );
};

export default HomePage;
