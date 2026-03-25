import React, { useState, useEffect } from 'react';
import { Settings, Cpu, Key, Download, CheckCircle, XCircle, Loader2, BarChart3 } from 'lucide-react';
import { apiService } from '../services/api';

interface LLMConfig {
  provider: 'local' | 'openai';
  model: string;
  openaiApiKey?: string;
  temperature: number;
  maxTokens: number;
  topP: number;
}

interface RAGConfig {
  chunkSize: number;
  overlap: number;
  topK: number;
  vectorWeight: number;
  keywordWeight: number;
  rerankTopK: number;
}

export const LLMConfig: React.FC = () => {
  const [llmConfig, setLLMConfig] = useState<LLMConfig>({
    provider: 'local',
    model: 'llama2-7b',
    temperature: 0.7,
    maxTokens: 2048,
    topP: 0.9,
  });

  const [ragConfig, setRagConfig] = useState<RAGConfig>({
    chunkSize: 200,
    overlap: 25,
    topK: 5,
    vectorWeight: 0.5,
    keywordWeight: 0.5,
    rerankTopK: 10,
  });

  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [installingModel, setInstallingModel] = useState<string | null>(null);
  const [testingConnection, setTestingConnection] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [connectionMessage, setConnectionMessage] = useState('');

  const localModels = [
    'llama2-7b',
    'llama2-13b',
    'llama2-70b',
    'mistral-7b',
    'mixtral-8x7b',
    'codellama-7b',
    'codellama-13b',
    'qwen-7b',
    'qwen-14b',
  ];

  const openaiModels = [
    'gpt-3.5-turbo',
    'gpt-4',
    'gpt-4-turbo-preview',
    'gpt-4o',
    'gpt-4o-mini',
  ];

  useEffect(() => {
    fetchAvailableModels();
  }, []);

  const fetchAvailableModels = async () => {
    try {
      const models = await apiService.getAvailableModels();
      setAvailableModels(models);
    } catch (error) {
      console.error('Failed to fetch models:', error);
    }
  };

  const installModel = async (modelName: string) => {
    setInstallingModel(modelName);
    try {
      await apiService.installModel(modelName);
      await fetchAvailableModels();
      setConnectionMessage(`✅ Successfully installed ${modelName}`);
      setConnectionStatus('success');
    } catch (error: any) {
      setConnectionMessage(`❌ Failed to install ${modelName}: ${error.message}`);
      setConnectionStatus('error');
    } finally {
      setInstallingModel(null);
    }
  };

  const testConnection = async () => {
    setTestingConnection(true);
    setConnectionStatus('idle');
    try {
      await apiService.testLLMConnection(llmConfig);
      setConnectionMessage('✅ LLM connection successful!');
      setConnectionStatus('success');
    } catch (error: any) {
      setConnectionMessage(`❌ Connection failed: ${error.message}`);
      setConnectionStatus('error');
    } finally {
      setTestingConnection(false);
    }
  };

  const loadBestConfig = async () => {
    try {
      const result = await apiService.loadBestConfig();
      setRagConfig(result.rag_config);
      setLLMConfig(result.llm_config);
      setConnectionMessage(result.message);
      setConnectionStatus('success');
    } catch (error: any) {
      setConnectionMessage(`❌ Failed to load best config: ${error.message}`);
      setConnectionStatus('error');
    }
  };

  const saveConfig = async () => {
    try {
      await apiService.updateLLMConfig(llmConfig);
      await apiService.updateRAGConfig(ragConfig);
      setConnectionMessage('✅ Configuration saved successfully!');
      setConnectionStatus('success');
    } catch (error: any) {
      setConnectionMessage(`❌ Failed to save config: ${error.message}`);
      setConnectionStatus('error');
    }
  };

  const currentModels = llmConfig.provider === 'local' ? localModels : openaiModels;

  return (
    <div className="space-y-6">
      {/* LLM Configuration */}
      <div className="futuristic-card p-8">
        <h3 className="text-2xl font-bold text-futuristic mb-6 flex items-center">
          <Cpu className="w-6 h-6 mr-3 text-cyan-400" />
          Neural Core Configuration
        </h3>

        {/* Provider Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Provider</label>
          <div className="flex space-x-4">
            <label className="flex items-center">
              <input
                type="radio"
                value="local"
                checked={llmConfig.provider === 'local'}
                onChange={(e) => setLLMConfig({ ...llmConfig, provider: 'local' })}
                className="mr-2"
              />
              Local Models
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="openai"
                checked={llmConfig.provider === 'openai'}
                onChange={(e) => setLLMConfig({ ...llmConfig, provider: 'openai' })}
                className="mr-2"
              />
              OpenAI API
            </label>
          </div>
        </div>

        {/* Model Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Model</label>
          <select
            value={llmConfig.model}
            onChange={(e) => setLLMConfig({ ...llmConfig, model: e.target.value })}
            className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {currentModels.map((model) => (
              <option key={model} value={model}>
                {model} {availableModels.includes(model) ? '✅' : '📥'}
              </option>
            ))}
          </select>
        </div>

        {/* OpenAI API Key */}
        {llmConfig.provider === 'openai' && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Key className="w-4 h-4 inline mr-1" />
              API Key
            </label>
            <input
              type="password"
              value={llmConfig.openaiApiKey || ''}
              onChange={(e) => setLLMConfig({ ...llmConfig, openaiApiKey: e.target.value })}
              placeholder="sk-..."
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        )}

        {/* Model Installation for Local Models */}
        {llmConfig.provider === 'local' && !availableModels.includes(llmConfig.model) && (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800 mb-2">
              Model "{llmConfig.model}" is not installed locally.
            </p>
            <button
              onClick={() => installModel(llmConfig.model)}
              disabled={installingModel === llmConfig.model}
              className="bg-yellow-600 text-white py-2 px-4 rounded-lg hover:bg-yellow-700 disabled:bg-gray-400 flex items-center"
            >
              {installingModel === llmConfig.model ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Installing...
                </>
              ) : (
                <>
                  <Download className="w-4 h-4 mr-2" />
                  Install Model
                </>
              )}
            </button>
          </div>
        )}

        {/* LLM Parameters */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Temperature: {llmConfig.temperature.toFixed(2)}
            </label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.01"
              value={llmConfig.temperature}
              onChange={(e) => setLLMConfig({ ...llmConfig, temperature: parseFloat(e.target.value) })}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>0 (Focused)</span>
              <span>1 (Balanced)</span>
              <span>2 (Creative)</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Tokens: {llmConfig.maxTokens}
            </label>
            <input
              type="range"
              min="128"
              max="4096"
              step="128"
              value={llmConfig.maxTokens}
              onChange={(e) => setLLMConfig({ ...llmConfig, maxTokens: parseInt(e.target.value) })}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>128</span>
              <span>2048</span>
              <span>4096</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Top P: {llmConfig.topP.toFixed(2)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={llmConfig.topP}
              onChange={(e) => setLLMConfig({ ...llmConfig, topP: parseFloat(e.target.value) })}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>0 (Focused)</span>
              <span>0.5 (Balanced)</span>
              <span>1 (Diverse)</span>
            </div>
          </div>
        </div>
      </div>

      {/* RAG Configuration */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
          <Settings className="w-5 h-5 mr-2" />
          RAG Configuration
        </h3>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Chunk Size: {ragConfig.chunkSize}
            </label>
            <input
              type="range"
              min="100"
              max="1000"
              step="50"
              value={ragConfig.chunkSize}
              onChange={(e) => setRagConfig({ ...ragConfig, chunkSize: parseInt(e.target.value) })}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>100 (Small)</span>
              <span>500 (Medium)</span>
              <span>1000 (Large)</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Overlap: {ragConfig.overlap}
            </label>
            <input
              type="range"
              min="0"
              max="200"
              step="10"
              value={ragConfig.overlap}
              onChange={(e) => setRagConfig({ ...ragConfig, overlap: parseInt(e.target.value) })}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>0</span>
              <span>100</span>
              <span>200</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Top-K: {ragConfig.topK}
            </label>
            <input
              type="range"
              min="1"
              max="20"
              step="1"
              value={ragConfig.topK}
              onChange={(e) => setRagConfig({ ...ragConfig, topK: parseInt(e.target.value) })}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>1</span>
              <span>10</span>
              <span>20</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Vector Weight: {ragConfig.vectorWeight.toFixed(2)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={ragConfig.vectorWeight}
              onChange={(e) => setRagConfig({ ...ragConfig, vectorWeight: parseFloat(e.target.value) })}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>0 (Keywords Only)</span>
              <span>0.5 (Balanced)</span>
              <span>1 (Vector Only)</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Keyword Weight: {ragConfig.keywordWeight.toFixed(2)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={ragConfig.keywordWeight}
              onChange={(e) => setRagConfig({ ...ragConfig, keywordWeight: parseFloat(e.target.value) })}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>0 (Vector Only)</span>
              <span>0.5 (Balanced)</span>
              <span>1 (Keywords Only)</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Rerank Top-K: {ragConfig.rerankTopK}
            </label>
            <input
              type="range"
              min="5"
              max="50"
              step="5"
              value={ragConfig.rerankTopK}
              onChange={(e) => setRagConfig({ ...ragConfig, rerankTopK: parseInt(e.target.value) })}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>5</span>
              <span>25</span>
              <span>50</span>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-4">
        <button
          onClick={testConnection}
          disabled={testingConnection}
          className="futuristic-btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {testingConnection ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 futuristic-spinner" />
              Testing...
            </>
          ) : (
            'Test Connection'
          )}
        </button>

        <button
          onClick={loadBestConfig}
          className="futuristic-btn-secondary"
        >
          <BarChart3 className="w-5 h-5 mr-2" />
          Load Best Config
        </button>

        <button
          onClick={saveConfig}
          className="futuristic-btn-success"
        >
          <Settings className="w-5 h-5 mr-2" />
          Save Configuration
        </button>
      </div>

      {/* Status Messages */}
      {connectionStatus !== 'idle' && (
        <div className={`p-4 rounded-lg flex items-center space-x-2 ${
          connectionStatus === 'success' ? 'futuristic-success' :
          'futuristic-error'
        }`}>
          {connectionStatus === 'success' ? <CheckCircle className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
          <span>{connectionMessage}</span>
        </div>
      )}
    </div>
  );
};
