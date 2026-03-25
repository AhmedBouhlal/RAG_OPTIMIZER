import React, { useState } from 'react';
import { CheckCircle, XCircle, Loader2, Wifi } from 'lucide-react';
import { apiService } from '../services/api';

export const ConnectionTest: React.FC = () => {
  const [status, setStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState<string>('');

  const testConnection = async () => {
    setStatus('testing');
    setMessage('Testing API connection...');

    try {
      // Test basic API connectivity
      await apiService.getStats();

      // Test query functionality
      const queryResult = await apiService.queryRAG({ query: 'test connection' });

      setStatus('success');
      setMessage('✅ Neural link established! All systems operational.');
    } catch (error: any) {
      setStatus('error');
      setMessage(`❌ Connection failed: ${error.message}`);
    }
  };

  return (
    <div className="futuristic-card p-8">
      <h3 className="text-2xl font-bold text-futuristic mb-6 flex items-center">
        <Wifi className="w-6 h-6 mr-3 text-cyan-400" />
        Neural Link Diagnostics
      </h3>

      <div className="space-y-6">
        <button
          onClick={testConnection}
          disabled={status === 'testing'}
          className="futuristic-btn-primary w-full py-4 text-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {status === 'testing' ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 futuristic-spinner" />
              Scanning Neural Pathways...
            </>
          ) : (
            <>
              <Wifi className="w-5 h-5 mr-2" />
              Initialize Connection Test
            </>
          )}
        </button>

        {status !== 'idle' && (
          <div className={`p-4 rounded-lg flex items-center space-x-2 ${
            status === 'success' ? 'futuristic-success' :
            status === 'error' ? 'futuristic-error' :
            'futuristic-warning'
          }`}>
            {status === 'success' && <CheckCircle className="w-5 h-5" />}
            {status === 'error' && <XCircle className="w-5 h-5" />}
            {status === 'testing' && <Loader2 className="w-5 h-5 futuristic-spinner" />}
            <span>{message}</span>
          </div>
        )}
      </div>
    </div>
  );
};
