// src/main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App.jsx';
import { SelectedPDFProvider } from './context/selectedPDFContext.jsx';

ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <SelectedPDFProvider>
      <App />
    </SelectedPDFProvider>
  </BrowserRouter>
);
