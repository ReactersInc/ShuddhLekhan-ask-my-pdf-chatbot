import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import PDFViewerPage from "./pages/PDFviewerPage";
import { SelectedPDFProvider } from "./context/selectedPDFContext";

ReactDOM.createRoot(document.getElementById("root")).render(
  <SelectedPDFProvider>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/pdf/:name?" element={<PDFViewerPage />} />
        </Routes>
    </BrowserRouter>
  </SelectedPDFProvider>
);
