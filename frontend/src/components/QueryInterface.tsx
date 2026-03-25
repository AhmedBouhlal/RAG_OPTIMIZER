import React, { useState } from 'react';
import { Search, Loader2, FileText, BarChart3 } from 'lucide-react';
import { apiService } from '../services/api';
import { QueryResponse } from '../types';

interface QueryInterfaceProps {
  onResponse: (response: QueryResponse) => void;
}

export const QueryInterface: React.FC<QueryInterfaceProps> = ({ onResponse }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.queryRAG({ query });
      onResponse(response);
      setQuery('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred while querying the RAG system');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center mb-4">
        <Search className="w-6 h-6 text-blue-600 mr-2" />
        <h2 className="text-xl font-semibold text-gray-800">Query RAG System</h2>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your question about the documents..."
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows={4}
            disabled={loading}
          />
        </div>
        
        <button
          type="submit"
          disabled={!query.trim() || loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center transition-colors"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Search className="w-4 h-4 mr-2" />
              Submit Query
            </>
          )}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}
    </div>
  );
};
