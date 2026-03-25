import React from 'react';
import { FileText, BarChart3, Clock } from 'lucide-react';
import { QueryResponse } from '../types';

interface QueryResponseProps {
  response: QueryResponse | null;
}

export const QueryResponseDisplay: React.FC<QueryResponseProps> = ({ response }) => {
  if (!response) return null;

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mt-6">
      <div className="flex items-center mb-4">
        <FileText className="w-6 h-6 text-green-600 mr-2" />
        <h2 className="text-xl font-semibold text-gray-800">Response</h2>
      </div>

      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-medium text-gray-700 mb-2">Answer</h3>
          <div className="p-4 bg-gray-50 rounded-lg">
            <p className="text-gray-800 whitespace-pre-wrap">{response.answer}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h3 className="text-lg font-medium text-gray-700 mb-2 flex items-center">
              <BarChart3 className="w-5 h-5 mr-2" />
              Confidence Score
            </h3>
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center">
                <div className="flex-1 bg-gray-200 rounded-full h-2 mr-3">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(response.confidence || 0) * 100}%` }}
                  />
                </div>
                <span className="text-sm font-medium text-blue-800">
                  {Math.round((response.confidence || 0) * 100)}%
                </span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-medium text-gray-700 mb-2">Sources</h3>
            <div className="p-4 bg-green-50 rounded-lg">
              {response.sources && response.sources.length > 0 ? (
                <ul className="space-y-1">
                  {response.sources.map((source, index) => (
                    <li key={index} className="text-sm text-gray-700 truncate">
                      • {source}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-500">No sources available</p>
              )}
            </div>
          </div>
        </div>

        {response.meta && (
          <div>
            <h3 className="text-lg font-medium text-gray-700 mb-2 flex items-center">
              <Clock className="w-5 h-5 mr-2" />
              Metadata
            </h3>
            <div className="p-4 bg-yellow-50 rounded-lg">
              <pre className="text-xs text-gray-700 overflow-x-auto">
                {JSON.stringify(response.meta, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
