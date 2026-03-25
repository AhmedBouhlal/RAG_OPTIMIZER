import React, { useState, useEffect } from 'react';
import { BarChart3, Clock, TrendingUp, Trash2, RefreshCw, Loader2 } from 'lucide-react';
import { apiService } from '../services/api';
import { Stats, HistoryItem } from '../types';

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [statsData, historyData] = await Promise.all([
        apiService.getStats(),
        apiService.getHistory()
      ]);
      setStats(statsData);
      setHistory(historyData);
    } catch (error: any) {
      setError('Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = async () => {
    try {
      await apiService.clearHistory();
      setHistory([]);
    } catch (error: any) {
      setError('Failed to clear history');
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-center py-8">
          <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center">
            <BarChart3 className="w-6 h-6 text-indigo-600 mr-2" />
            <h2 className="text-xl font-semibold text-gray-800">System Statistics</h2>
          </div>
          <button
            onClick={fetchDashboardData}
            className="text-indigo-600 hover:text-indigo-700"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>

        {stats ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-blue-600 font-medium">Total Queries</p>
                  <p className="text-2xl font-bold text-blue-800">{stats.queries}</p>
                </div>
                <BarChart3 className="w-8 h-8 text-blue-400" />
              </div>
            </div>

            <div className="bg-green-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-green-600 font-medium">Avg Response Time</p>
                  <p className="text-2xl font-bold text-green-800">{stats.avg_time.toFixed(2)}s</p>
                </div>
                <Clock className="w-8 h-8 text-green-400" />
              </div>
            </div>

            <div className="bg-purple-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-purple-600 font-medium">Cache Hit Rate</p>
                  <p className="text-2xl font-bold text-purple-800">{(stats.cache_hit_rate * 100).toFixed(1)}%</p>
                </div>
                <TrendingUp className="w-8 h-8 text-purple-400" />
              </div>
            </div>

            <div className="bg-red-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-red-600 font-medium">Error Rate</p>
                  <p className="text-2xl font-bold text-red-800">{(stats.error_rate * 100).toFixed(1)}%</p>
                </div>
                <Trash2 className="w-8 h-8 text-red-400" />
              </div>
            </div>
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">No statistics available</p>
        )}
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center">
            <Clock className="w-6 h-6 text-teal-600 mr-2" />
            <h2 className="text-xl font-semibold text-gray-800">Query History</h2>
          </div>
          <div className="flex items-center space-x-2">
            {history.length > 0 && (
              <button
                onClick={clearHistory}
                className="text-red-600 hover:text-red-700 px-3 py-1 text-sm border border-red-300 rounded hover:bg-red-50"
              >
                Clear History
              </button>
            )}
            <button
              onClick={fetchDashboardData}
              className="text-teal-600 hover:text-teal-700"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
          </div>
        </div>

        {history.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Clock className="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p>No query history available</p>
          </div>
        ) : (
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {history.map((item, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-medium text-gray-800 flex-1">Q: {item.query}</h4>
                  <span className="text-xs text-gray-500 ml-2">
                    {new Date(item.timestamp).toLocaleString()}
                  </span>
                </div>
                <div className="text-gray-700 text-sm">
                  <span className="font-medium">A:</span> {item.answer}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error}
        </div>
      )}
    </div>
  );
};
