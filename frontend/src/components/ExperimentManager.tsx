import React, { useState, useEffect } from 'react';
import { Play, RefreshCw, CheckCircle, XCircle, Clock, Loader2, BarChart3 } from 'lucide-react';
import { apiService } from '../services/api';
import { ExperimentJob } from '../types';

export const ExperimentManager: React.FC = () => {
  const [jobs, setJobs] = useState<Record<string, ExperimentJob>>({});
  const [loading, setLoading] = useState(false);
  const [selectedMode, setSelectedMode] = useState<'sample' | 'comprehensive'>('sample');
  const [selectedJob, setSelectedJob] = useState<ExperimentJob | null>(null);
  const [jobResults, setJobResults] = useState<any>(null);

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchJobs = async () => {
    try {
      const jobsData = await apiService.getExperiments();
      setJobs(jobsData);
    } catch (error) {
      console.error('Failed to fetch jobs:', error);
    }
  };

  const startExperiment = async () => {
    setLoading(true);
    try {
      const response = await apiService.startExperiment({ mode: selectedMode });
      await fetchJobs();
    } catch (error: any) {
      console.error('Failed to start experiment:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchJobResults = async (jobId: string) => {
    try {
      const results = await apiService.getExperimentResults(jobId);
      setJobResults(results);
    } catch (error: any) {
      console.error('Failed to fetch results:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'queued':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'running':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'queued':
        return 'bg-yellow-100 text-yellow-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center mb-6">
        <BarChart3 className="w-6 h-6 text-purple-600 mr-2" />
        <h2 className="text-xl font-semibold text-gray-800">Experiment Manager</h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-medium text-gray-700 mb-4">Start New Experiment</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Experiment Mode
              </label>
              <select
                value={selectedMode}
                onChange={(e) => setSelectedMode(e.target.value as 'sample' | 'comprehensive')}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="sample">Sample (Quick)</option>
                <option value="comprehensive">Comprehensive (Full)</option>
              </select>
            </div>
            
            <button
              onClick={startExperiment}
              disabled={loading}
              className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center transition-colors"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Starting...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Start {selectedMode === 'sample' ? 'Sample' : 'Comprehensive'} Experiment
                </>
              )}
            </button>
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-700">Experiment Jobs</h3>
            <button
              onClick={fetchJobs}
              className="text-purple-600 hover:text-purple-700"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
          
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {Object.entries(jobs).length === 0 ? (
              <p className="text-gray-500 text-center py-4">No experiments started yet</p>
            ) : (
              Object.entries(jobs).map(([jobId, job]) => (
                <div
                  key={jobId}
                  className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                    selectedJob?.job_id === jobId ? 'border-purple-500 bg-purple-50' : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => {
                    setSelectedJob(job);
                    if (job.status === 'completed') {
                      fetchJobResults(jobId);
                    } else {
                      setJobResults(null);
                    }
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(job.status)}
                      <span className={`text-xs font-medium px-2 py-1 rounded-full ${getStatusColor(job.status)}`}>
                        {job.status}
                      </span>
                    </div>
                    <span className="text-xs text-gray-500">{job.mode}</span>
                  </div>
                  <div className="mt-1">
                    <p className="text-xs text-gray-600 truncate">{jobId}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {selectedJob && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h3 className="text-lg font-medium text-gray-700 mb-4">Selected Job Details</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium text-gray-600">Job ID:</span>
                <p className="text-gray-800 break-all">{selectedJob.job_id}</p>
              </div>
              <div>
                <span className="font-medium text-gray-600">Mode:</span>
                <p className="text-gray-800">{selectedJob.mode}</p>
              </div>
              <div>
                <span className="font-medium text-gray-600">Status:</span>
                <div className="flex items-center mt-1">
                  {getStatusIcon(selectedJob.status)}
                  <span className="ml-1">{selectedJob.status}</span>
                </div>
              </div>
              {selectedJob.error && (
                <div>
                  <span className="font-medium text-gray-600">Error:</span>
                  <p className="text-red-600 text-xs mt-1">{selectedJob.error}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {jobResults && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h3 className="text-lg font-medium text-gray-700 mb-4">Experiment Results</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <pre className="text-xs text-gray-700 overflow-x-auto">
              {JSON.stringify(jobResults, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};
