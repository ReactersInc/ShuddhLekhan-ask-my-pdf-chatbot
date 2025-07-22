// src/pages/HomePage.jsx
import React from 'react';
import UploadPDF from '../components/UploadPDF';
import PDFList from '../components/PDFList';
// import AskQuestion from '../components/AskQuestion';

const HomePage = () => {
  return (
    <div>
      <h1>AI PDF Summarizer Chatbot</h1>
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
