/**
 * API Test Page
 * 
 * Simple page to test the API client functions.
 * Navigate to /api-test to use this page.
 */

'use client';

import { useState } from 'react';
import { useResearchQuestions, useResearchSession } from '@/lib/use-research';
import { ResearchPhase } from '@/lib/api-client';

export default function ApiTestPage() {
  const { questions, loading: questionsLoading } = useResearchQuestions();
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  const {
    sessionId,
    status,
    result,
    error,
    isStarting,
    isRunning,
    isCompleted,
    progressPercentage,
    currentAgent,
    start,
    reset,
  } = useResearchSession({
    onProgress: (status) => {
      addLog(`Progress: ${status.progress_percentage}% - ${status.current_agent || 'Starting...'}`);
    },
    onComplete: (result) => {
      addLog(`✅ Research completed in ${result.execution_time_seconds.toFixed(2)}s`);
      addLog(`📊 Collected ${result.total_data_points} data points`);
    },
    onError: (error) => {
      addLog(`❌ Error: ${error.message}`);
    },
  });

  const handleStartResearch = async (questionId: string) => {
    addLog(`🚀 Starting research: ${questionId}`);
    reset();
    setLogs([]);
    await start({
      question_id: questionId,
      conversation_id: 'test-conversation',
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-gray-900 dark:text-white">
          API Test Page
        </h1>

        {/* Questions Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            Available Research Questions
          </h2>
          
          {questionsLoading ? (
            <p className="text-gray-600 dark:text-gray-400">Loading questions...</p>
          ) : (
            <div className="grid gap-3">
              {questions.map((q) => (
                <button
                  key={q.id}
                  onClick={() => handleStartResearch(q.id)}
                  disabled={isStarting || isRunning}
                  className="text-left p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <div className="font-medium text-gray-900 dark:text-white">{q.title}</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">{q.question}</div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Status Section */}
        {sessionId && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
              Research Status
            </h2>
            
            <div className="space-y-3">
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">Session ID:</span>
                <span className="ml-2 text-gray-600 dark:text-gray-400 font-mono text-sm">{sessionId}</span>
              </div>

              {status && (
                <>
                  <div>
                    <span className="font-medium text-gray-700 dark:text-gray-300">Phase:</span>
                    <span className="ml-2 text-gray-600 dark:text-gray-400">{status.phase}</span>
                  </div>

                  <div>
                    <span className="font-medium text-gray-700 dark:text-gray-300">Progress:</span>
                    <span className="ml-2 text-gray-600 dark:text-gray-400">{progressPercentage}%</span>
                  </div>

                  {currentAgent && (
                    <div>
                      <span className="font-medium text-gray-700 dark:text-gray-300">Current Agent:</span>
                      <span className="ml-2 text-gray-600 dark:text-gray-400">{currentAgent}</span>
                    </div>
                  )}

                  {/* Progress Bar */}
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${progressPercentage}%` }}
                    />
                  </div>
                </>
              )}

              {error && (
                <div className="text-red-600 dark:text-red-400 p-3 bg-red-50 dark:bg-red-900/20 rounded">
                  {error}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Result Section */}
        {result && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
              Research Result
            </h2>
            
            <div className="space-y-4">
              <div>
                <h3 className="font-medium text-gray-700 dark:text-gray-300 mb-2">Executive Summary</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  {result.executive_summary || 'Not available (Azure OpenAI not configured)'}
                </p>
              </div>

              <div>
                <h3 className="font-medium text-gray-700 dark:text-gray-300 mb-2">Data Collected</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                  <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded">
                    <div className="text-gray-500 dark:text-gray-500">Twitter</div>
                    <div className="text-lg font-semibold text-gray-900 dark:text-white">
                      {result.data_collected.social_media.twitter.total_results}
                    </div>
                  </div>
                  <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded">
                    <div className="text-gray-500 dark:text-gray-500">TikTok</div>
                    <div className="text-lg font-semibold text-gray-900 dark:text-white">
                      {result.data_collected.social_media.tiktok.total_results}
                    </div>
                  </div>
                  <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded">
                    <div className="text-gray-500 dark:text-gray-500">Reddit</div>
                    <div className="text-lg font-semibold text-gray-900 dark:text-white">
                      {result.data_collected.social_media.reddit.total_results}
                    </div>
                  </div>
                  <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded">
                    <div className="text-gray-500 dark:text-gray-500">Web Search</div>
                    <div className="text-lg font-semibold text-gray-900 dark:text-white">
                      {result.data_collected.web_intelligence.total_results}
                    </div>
                  </div>
                  <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded">
                    <div className="text-gray-500 dark:text-gray-500">Total Points</div>
                    <div className="text-lg font-semibold text-gray-900 dark:text-white">
                      {result.total_data_points}
                    </div>
                  </div>
                  <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded">
                    <div className="text-gray-500 dark:text-gray-500">Time</div>
                    <div className="text-lg font-semibold text-gray-900 dark:text-white">
                      {result.execution_time_seconds.toFixed(1)}s
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Logs Section */}
        {logs.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
              Activity Log
            </h2>
            <div className="bg-gray-50 dark:bg-gray-900 rounded p-4 font-mono text-xs space-y-1 max-h-64 overflow-y-auto">
              {logs.map((log, i) => (
                <div key={i} className="text-gray-700 dark:text-gray-300">
                  {log}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
