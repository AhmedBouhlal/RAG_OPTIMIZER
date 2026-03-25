import React, { useState } from 'react';
import { Send, Loader2, XCircle } from 'lucide-react';
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
      setError(err.message || 'Failed to process query');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="futuristic-card p-8">
      <h3 className="text-2xl font-bold text-futuristic mb-6">Neural Query Interface</h3>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-cyan-400 mb-2">
            Enter your query
          </label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask me anything about the documents..."
            className="futuristic-textarea w-full"
            rows={4}
            disabled={loading}
          />
        </div>

        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="futuristic-btn-primary w-full py-4 text-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 futuristic-spinner" />
              Processing...
            </>
          ) : (
            <>
              <Send className="w-5 h-5 mr-2" />
              Transmit Query
            </>
          )}
        </button>
      </form>

      {error && (
        <div className="futuristic-error p-4 rounded-lg flex items-center space-x-2 mt-4">
          <XCircle className="w-5 h-5" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};
