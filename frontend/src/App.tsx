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
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-16'} bg-white shadow-lg transition-all duration-300 flex flex-col`}>
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            {sidebarOpen && (
              <h1 className="text-xl font-bold text-gray-800">RAG System</h1>
            )}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <li key={tab.id}>
                  <button
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center px-3 py-2 rounded-lg transition-colors ${
                      activeTab === tab.id
                        ? getActiveTabColor(tab.color)
                        : getTabColor(tab.color)
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    {sidebarOpen && <span className="ml-3">{tab.label}</span>}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold text-gray-800">
              {tabs.find(tab => tab.id === activeTab)?.label}
            </h2>
            <div className="text-sm text-gray-500">
              RAG System Dashboard
            </div>
          </div>
        </header>

        <main className="flex-1 p-6 overflow-auto">
          <div className="max-w-7xl mx-auto">
            {activeTab === 'query' && (
              <div className="space-y-6">
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
