import React, { useState } from 'react';
import { QueryInterface } from './components/QueryInterface';
import { QueryResponseDisplay } from './components/QueryResponse';
import { ExperimentManager } from './components/ExperimentManager';
import { DocumentManager } from './components/DocumentManager';
import { EvaluationManager } from './components/EvaluationManager';
import { Dashboard } from './components/Dashboard';
import { ConnectionTest } from './components/ConnectionTest';
import { LLMConfig } from './components/LLMConfig';
import { QueryResponse } from './types';
import { Search, BarChart3, FileText, FileJson, LayoutDashboard, Menu, X, Wifi, Settings } from 'lucide-react';

type TabType = 'query' | 'experiments' | 'documents' | 'evaluation' | 'dashboard' | 'connection' | 'llm-config';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('query');
  const [queryResponse, setQueryResponse] = useState<QueryResponse | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const tabs = [
    { id: 'query' as TabType, label: 'Query RAG', icon: Search, color: 'blue' },
    { id: 'experiments' as TabType, label: 'Experiments', icon: BarChart3, color: 'purple' },
    { id: 'documents' as TabType, label: 'Documents', icon: FileText, color: 'green' },
    { id: 'evaluation' as TabType, label: 'Evaluation', icon: FileJson, color: 'orange' },
    { id: 'dashboard' as TabType, label: 'Dashboard', icon: LayoutDashboard, color: 'indigo' },
    { id: 'llm-config' as TabType, label: 'LLM Config', icon: Settings, color: 'red' },
    { id: 'connection' as TabType, label: 'Connection Test', icon: Wifi, color: 'gray' },
  ];

  const getTabColor = (color: string) => {
    const colors = {
      blue: 'text-blue-600 hover:bg-blue-50',
      purple: 'text-purple-600 hover:bg-purple-50',
      green: 'text-green-600 hover:bg-green-50',
      orange: 'text-orange-600 hover:bg-orange-50',
      indigo: 'text-indigo-600 hover:bg-indigo-50',
      red: 'text-red-600 hover:bg-red-50',
      gray: 'text-gray-600 hover:bg-gray-50',
    };
    return colors[color as keyof typeof colors] || colors.blue;
  };

  const getActiveTabColor = (color: string) => {
    const colors = {
      blue: 'bg-blue-100 text-blue-700 border-r-2 border-blue-600',
      purple: 'bg-purple-100 text-purple-700 border-r-2 border-purple-600',
      green: 'bg-green-100 text-green-700 border-r-2 border-green-600',
      orange: 'bg-orange-100 text-orange-700 border-r-2 border-orange-600',
      indigo: 'bg-indigo-100 text-indigo-700 border-r-2 border-indigo-600',
      red: 'bg-red-100 text-red-700 border-r-2 border-red-600',
      gray: 'bg-gray-100 text-gray-700 border-r-2 border-gray-600',
    };
    return colors[color as keyof typeof colors] || colors.blue;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 flex" style={{background: 'linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)'}}>
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-72' : 'w-20'} futuristic-sidebar transition-all duration-500 flex flex-col`}>
        <div className="p-6 border-b border-cyan-500/20">
          <div className="flex items-center justify-between">
            {sidebarOpen && (
              <h1 className="text-2xl font-bold text-futuristic">RAG SYSTEM</h1>
            )}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-3 rounded-lg hover:bg-gray-800/50 transition-all duration-300 text-cyan-400 hover:text-cyan-300"
            >
              {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center futuristic-tab transition-all duration-300 ${
                  activeTab === tab.id ? 'futuristic-tab-active' : ''
                }`}
              >
                <Icon className="w-5 h-5" />
                {sidebarOpen && <span className="ml-3 font-medium">{tab.label}</span>}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col" style={{backgroundColor: 'transparent'}}>
        <header className="futuristic-header px-8 py-6">
          <div className="flex items-center justify-between">
            <h2 className="text-3xl font-bold text-futuristic">
              {tabs.find(tab => tab.id === activeTab)?.label}
            </h2>
            <div className="flex items-center space-x-2">
              <div className="futuristic-badge animate-pulse-glow">ONLINE</div>
              <div className="text-sm text-gray-400">RAG Neural Interface</div>
            </div>
          </div>
        </header>

        <main className="flex-1 p-8 overflow-auto" style={{backgroundColor: 'transparent'}}>
          <div className="max-w-7xl mx-auto">
            {activeTab === 'query' && (
              <div className="space-y-8">
                <QueryInterface onResponse={setQueryResponse} />
                <QueryResponseDisplay response={queryResponse} />
              </div>
            )}

            {activeTab === 'experiments' && <ExperimentManager />}
            {activeTab === 'documents' && <DocumentManager />}
            {activeTab === 'evaluation' && <EvaluationManager />}
            {activeTab === 'dashboard' && <Dashboard />}
            {activeTab === 'llm-config' && <LLMConfig />}
            {activeTab === 'connection' && <ConnectionTest />}
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;
