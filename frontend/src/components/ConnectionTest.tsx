import React, { useState } from 'react';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';
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
      setMessage('✅ API connection successful! All systems working.');
    } catch (error: any) {
      setStatus('error');
      setMessage(`❌ Connection failed: ${error.message}`);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">API Connection Test</h3>
      
      <div className="space-y-4">
        <button
          onClick={testConnection}
          disabled={status === 'testing'}
          className="bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center"
        >
          {status === 'testing' ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Testing...
            </>
          ) : (
            'Test Connection'
          )}
        </button>
        
        {status !== 'idle' && (
          <div className={`p-4 rounded-lg flex items-center space-x-2 ${
            status === 'success' ? 'bg-green-50 text-green-800' :
            status === 'error' ? 'bg-red-50 text-red-800' :
            'bg-blue-50 text-blue-800'
          }`}>
            {status === 'success' && <CheckCircle className="w-5 h-5" />}
            {status === 'error' && <XCircle className="w-5 h-5" />}
            {status === 'testing' && <Loader2 className="w-5 h-5 animate-spin" />}
            <span>{message}</span>
          </div>
        )}
      </div>
    </div>
  );
};
