export interface QueryRequest {
  query: string;
}

export interface QueryResponse {
  answer: string;
  confidence: number;
  sources: string[];
  meta: any;
}

export interface ExperimentRequest {
  mode: 'sample' | 'comprehensive';
}

export interface ExperimentJob {
  job_id: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  mode: string;
  result?: any;
  error?: string;
}

export interface Document {
  filename: string;
  path?: string;
}

export interface EvaluationFile {
  filename: string;
  path?: string;
}

export interface Stats {
  queries: number;
  avg_time: number;
  cache_hit_rate: number;
  error_rate: number;
}

export interface HistoryItem {
  query: string;
  answer: string;
  timestamp: string;
}
