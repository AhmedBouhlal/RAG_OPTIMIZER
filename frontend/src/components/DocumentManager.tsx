import React, { useState, useEffect } from 'react';
import { Upload, FileText, Trash2, RefreshCw, Loader2 } from 'lucide-react';
import { apiService } from '../services/api';

export const DocumentManager: React.FC = () => {
  const [documents, setDocuments] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const response = await apiService.getDocuments();
      setDocuments(response.documents);
    } catch (error: any) {
      setError('Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);
    
    try {
      await apiService.uploadDocument(file);
      await fetchDocuments();
      e.target.value = '';
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (filename: string) => {
    try {
      await apiService.deleteDocument(filename);
      await fetchDocuments();
    } catch (error: any) {
      setError('Failed to delete document');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <FileText className="w-6 h-6 text-green-600 mr-2" />
          <h2 className="text-xl font-semibold text-gray-800">Document Management</h2>
        </div>
        <button
          onClick={fetchDocuments}
          disabled={loading}
          className="text-green-600 hover:text-green-700 disabled:text-gray-400"
        >
          <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-medium text-gray-700 mb-3">Upload Document</h3>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
            <input
              type="file"
              id="document-upload"
              onChange={handleFileUpload}
              disabled={uploading}
              className="hidden"
            />
            <label
              htmlFor="document-upload"
              className="cursor-pointer flex flex-col items-center space-y-2"
            >
              {uploading ? (
                <Loader2 className="w-8 h-8 text-gray-400 animate-spin" />
              ) : (
                <Upload className="w-8 h-8 text-gray-400" />
              )}
              <span className="text-sm text-gray-600">
                {uploading ? 'Uploading...' : 'Click to upload or drag and drop'}
              </span>
              <span className="text-xs text-gray-500">
                Supports: TXT, PDF, DOCX, MD, HTML
              </span>
            </label>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-medium text-gray-700 mb-3">
            Documents ({documents.length})
          </h3>
          {loading ? (
            <div className="flex justify-center py-4">
              <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-2 text-gray-300" />
              <p>No documents uploaded yet</p>
            </div>
          ) : (
            <div className="space-y-2">
              {documents.map((filename) => (
                <div
                  key={filename}
                  className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                >
                  <div className="flex items-center space-x-3">
                    <FileText className="w-5 h-5 text-gray-400" />
                    <span className="text-sm font-medium text-gray-700 truncate">
                      {filename}
                    </span>
                  </div>
                  <button
                    onClick={() => handleDelete(filename)}
                    className="text-red-500 hover:text-red-700 p-1 rounded hover:bg-red-50"
                    title="Delete document"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}
    </div>
  );
};
