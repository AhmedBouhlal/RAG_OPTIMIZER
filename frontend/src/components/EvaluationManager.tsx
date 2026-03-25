import React, { useState, useEffect } from 'react';
import { Upload, FileJson, Trash2, RefreshCw, Loader2 } from 'lucide-react';
import { apiService } from '../services/api';

export const EvaluationManager: React.FC = () => {
  const [evaluationFiles, setEvaluationFiles] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchEvaluationFiles();
  }, []);

  const fetchEvaluationFiles = async () => {
    setLoading(true);
    try {
      const response = await apiService.getEvaluationFiles();
      setEvaluationFiles(response.evaluation_files);
    } catch (error: any) {
      setError('Failed to fetch evaluation files');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.json')) {
      setError('Only JSON files are allowed for evaluation');
      return;
    }

    setUploading(true);
    setError(null);
    
    try {
      await apiService.uploadEvaluation(file);
      await fetchEvaluationFiles();
      e.target.value = '';
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to upload evaluation file');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (filename: string) => {
    try {
      await apiService.deleteEvaluation(filename);
      await fetchEvaluationFiles();
    } catch (error: any) {
      setError('Failed to delete evaluation file');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <FileJson className="w-6 h-6 text-orange-600 mr-2" />
          <h2 className="text-xl font-semibold text-gray-800">Evaluation Management</h2>
        </div>
        <button
          onClick={fetchEvaluationFiles}
          disabled={loading}
          className="text-orange-600 hover:text-orange-700 disabled:text-gray-400"
        >
          <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-medium text-gray-700 mb-3">Upload Evaluation File</h3>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
            <input
              type="file"
              id="evaluation-upload"
              onChange={handleFileUpload}
              disabled={uploading}
              accept=".json"
              className="hidden"
            />
            <label
              htmlFor="evaluation-upload"
              className="cursor-pointer flex flex-col items-center space-y-2"
            >
              {uploading ? (
                <Loader2 className="w-8 h-8 text-gray-400 animate-spin" />
              ) : (
                <Upload className="w-8 h-8 text-gray-400" />
              )}
              <span className="text-sm text-gray-600">
                {uploading ? 'Uploading...' : 'Click to upload JSON evaluation file'}
              </span>
              <span className="text-xs text-gray-500">
                Only JSON files are supported
              </span>
            </label>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-medium text-gray-700 mb-3">
            Evaluation Files ({evaluationFiles.length})
          </h3>
          {loading ? (
            <div className="flex justify-center py-4">
              <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
            </div>
          ) : evaluationFiles.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <FileJson className="w-12 h-12 mx-auto mb-2 text-gray-300" />
              <p>No evaluation files uploaded yet</p>
            </div>
          ) : (
            <div className="space-y-2">
              {evaluationFiles.map((filename) => (
                <div
                  key={filename}
                  className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                >
                  <div className="flex items-center space-x-3">
                    <FileJson className="w-5 h-5 text-orange-400" />
                    <span className="text-sm font-medium text-gray-700 truncate">
                      {filename}
                    </span>
                  </div>
                  <button
                    onClick={() => handleDelete(filename)}
                    className="text-red-500 hover:text-red-700 p-1 rounded hover:bg-red-50"
                    title="Delete evaluation file"
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
