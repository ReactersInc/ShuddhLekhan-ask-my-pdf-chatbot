import React, { useState } from "react";
import { API_URL } from "../config.js"

function UploadPDF() {
    const [file, setFile] = useState(null)
    const [message, setMessage] = useState("");
    const handleFileChange = (e) => setFile(e.target.files[0])

    const handleUpload = async () => {
        if (!file) {
            setMessage("Please select a file first");
            return;
        }
    
        const formData = new FormData(); 
        formData.append("file", file);
    
        try {
            const res = await fetch(`${API_URL}/upload/`, {
                method: "POST",
                body: formData,
            });
    
            const data = await res.json();
            if (res.ok) {
                setMessage(data.message);
                setFile(null);
            } else {
                setMessage(data.error || "File upload failed");
            }
        } catch (err) {
            setMessage("Error uploading file");
        }
    };
    
    return (
        <div>
          <h2>Upload PDF</h2>
          <input type="file" accept=".pdf" onChange={handleFileChange} />
          <button onClick={handleUpload}>Upload</button>
      
          {message && (
            <p className={message.includes("successfully") ? "success" : "error"}>
              {message}
            </p>
          )}
        </div>
      );
      
}

export default UploadPDF;

