import { useState } from "react";
import { API_URL } from "../config/config"
import { buildFolderTreeFromFiles } from '../utils/folderTreeBuilder';

const useFileUploader = () => {
    const [uploading, setUploading] = useState(false);
    const [message, setMessage] = useState('');
    const [uploadedPaths, setUploadedPaths] = useState([]);

    const uploadFiles = async (files) => {
        if (!files || files.length === 0) {
            setMessage('Please select at least one file')
            return
        }

        setUploading(true)
        setMessage('')
        setUploadedPaths([])

        const formData = new FormData();
        files.forEach(file => formData.append('files', file))

        try {
            const res = await fetch(`${API_URL}/dashboard/upload`, {
                method: 'POST',
                body: formData,
            })

            const data = await res.json()

            if (res.ok) {
                const folderTree = buildFolderTreeFromFiles(files);
                setMessage('Files uploaded successfully')
                setUploadedPaths(data.uploaded_files || [])
                return folderTree;
            }

            else {
                setMessage(data.error || 'Upload failed')
                return [];
            }
        }

        catch (error) {
            setMessage("Error uploading files")
            return [];
        }

        finally {
            setUploading(false)
        }
    }

    return {
        uploading,
        message,
        uploadedPaths,
        uploadFiles,
        setMessage,
    }
}

export default useFileUploader