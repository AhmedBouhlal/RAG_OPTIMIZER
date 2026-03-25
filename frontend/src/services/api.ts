import axios from 'axios';
import { QueryRequest, QueryResponse, ExperimentRequest, ExperimentJob, Document, EvaluationFile, Stats, HistoryItem } from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    if (error.response) {
      // Server responded with error status
      throw new Error(error.response.data?.detail || error.response.statusText || 'API request failed');
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Network error - unable to connect to API server');
    } else {
      // Something else happened
      throw new Error(error.message || 'Unknown error occurred');
    }
  }
);

export const apiService = {
  // Query endpoints
  async queryRAG(request: QueryRequest): Promise<QueryResponse> {
    const response = await api.post('/query', request);
    return response.data;
  },

  async getStats(): Promise<Stats> {
    const response = await api.get('/stats');
    return response.data;
  },

  async getHistory(): Promise<HistoryItem[]> {
    const response = await api.get('/history');
    return response.data;
  },

  async clearHistory(): Promise<{ message: string }> {
    const response = await api.delete('/history');
    return response.data;
  },

  // Experiment endpoints
  async startExperiment(request: ExperimentRequest): Promise<{ job_id: string; status: string; mode: string }> {
    const response = await api.post('/experiments/start', request);
    return response.data;
  },

  async getExperiments(): Promise<Record<string, ExperimentJob>> {
    const response = await api.get('/experiments');
    return response.data;
  },

  async getExperimentStatus(jobId: string): Promise<ExperimentJob> {
    const response = await api.get(`/experiments/${jobId}`);
    return response.data;
  },

  async getExperimentResults(jobId: string): Promise<any> {
    const response = await api.get(`/experiments/${jobId}/results`);
    return response.data;
  },

  // Document endpoints
  async uploadDocument(file: File): Promise<{ message: string; filename: string; path: string }> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      transformRequest: [(data, headers) => {
        // Let browser set Content-Type for FormData
        delete headers['Content-Type'];
        return data;
      }],
    });
    return response.data;
  },

  async getDocuments(): Promise<{ documents: string[] }> {
    const response = await api.get('/documents');
    return response.data;
  },

  async deleteDocument(filename: string): Promise<{ message: string }> {
    const response = await api.delete(`/documents/${filename}`);
    return response.data;
  },

  // Evaluation endpoints
  async uploadEvaluation(file: File): Promise<{ message: string; filename: string; path: string }> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/evaluation/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      transformRequest: [(data, headers) => {
        // Let browser set Content-Type for FormData
        delete headers['Content-Type'];
        return data;
      }],
    });
    return response.data;
  },

  async getEvaluationFiles(): Promise<{ evaluation_files: string[] }> {
    const response = await api.get('/evaluation');
    return response.data;
  },

  async deleteEvaluation(filename: string): Promise<{ message: string }> {
    const response = await api.delete(`/evaluation/${filename}`);
    return response.data;
  },
};
