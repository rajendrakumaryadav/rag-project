import React, { useState, useRef } from 'react';
import { Upload, File, X, Check, AlertCircle, FileText, Trash2 } from 'lucide-react';
import { documentAPI, Document } from '../../api/client';

interface DocumentUploadProps {
  onUploadComplete?: () => void;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadComplete }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [showDocuments, setShowDocuments] = useState(false);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadDocuments = async () => {
    setLoadingDocs(true);
    try {
      const response = await documentAPI.list();
      setDocuments(response.documents);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoadingDocs(false);
    }
  };

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadSuccess(false);
    setUploadError(null);

    try {
      await documentAPI.upload(file);
      setUploadSuccess(true);
      setTimeout(() => setUploadSuccess(false), 3000);
      onUploadComplete?.();
      
      // Reload documents if list is visible
      if (showDocuments) {
        await loadDocuments();
      }
    } catch (error: any) {
      setUploadError(error.response?.data?.detail || 'Failed to upload file');
      setTimeout(() => setUploadError(null), 5000);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDelete = async (filename: string) => {
    if (!window.confirm(`Delete "${filename}"?`)) return;

    try {
      await documentAPI.delete(filename);
      await loadDocuments();
    } catch (error) {
      console.error('Failed to delete document:', error);
      alert('Failed to delete document');
    }
  };

  const toggleDocuments = async () => {
    if (!showDocuments) {
      await loadDocuments();
    }
    setShowDocuments(!showDocuments);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="space-y-3">
      {/* Upload Button */}
      <div className="relative">
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileSelect}
          className="hidden"
          accept=".pdf,.txt,.docx,.doc,.md"
          disabled={uploading}
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-xl hover:from-emerald-600 hover:to-teal-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
        >
          {uploading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>Uploading...</span>
            </>
          ) : uploadSuccess ? (
            <>
              <Check className="h-5 w-5" />
              <span>Uploaded!</span>
            </>
          ) : (
            <>
              <Upload className="h-5 w-5" />
              <span>Upload Document</span>
            </>
          )}
        </button>
      </div>

      {/* Error Message */}
      {uploadError && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm animate-fadeIn">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          <span>{uploadError}</span>
        </div>
      )}

      {/* View Documents Button */}
      <button
        onClick={toggleDocuments}
        className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-white/50 border border-gray-200 text-gray-700 rounded-xl hover:bg-white transition-all duration-300 text-sm font-medium"
      >
        <FileText className="h-4 w-4" />
        <span>{showDocuments ? 'Hide' : 'View'} Documents ({documents.length})</span>
      </button>

      {/* Documents List */}
      {showDocuments && (
        <div className="bg-white/50 backdrop-blur-sm rounded-xl border border-gray-200 p-3 max-h-80 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent animate-fadeIn">
          {loadingDocs ? (
            <div className="flex items-center justify-center py-8 text-gray-500">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <File className="h-8 w-8 mx-auto mb-2 text-gray-400" />
              <p className="text-sm">No documents uploaded yet</p>
            </div>
          ) : (
            <div className="space-y-2">
              {documents.map((doc, index) => (
                <div
                  key={index}
                  className="group flex items-start justify-between gap-3 p-3 bg-white rounded-lg border border-gray-200 hover:border-emerald-200 hover:shadow-md transition-all duration-300"
                >
                  <div className="flex items-start gap-3 flex-1 min-w-0">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center flex-shrink-0">
                      <FileText className="h-5 w-5 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate text-sm">
                        {doc.name}
                      </p>
                      <div className="flex items-center gap-2 text-xs text-gray-500 mt-1">
                        <span>{formatFileSize(doc.size_bytes)}</span>
                        <span>•</span>
                        <span>{new Date(doc.uploaded_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDelete(doc.name)}
                    className="opacity-0 group-hover:opacity-100 transition-all duration-300 p-2 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-600 transform hover:scale-110"
                    title="Delete document"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Info Text */}
      <p className="text-xs text-gray-500 text-center">
        Supported: PDF, TXT, DOCX, MD
      </p>
    </div>
  );
};

export default DocumentUpload;
