/**
 * React Hooks for Research API
 * 
 * Custom hooks for managing research sessions in React components.
 * Handles state management, polling, and error handling.
 */

'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  startResearch,
  getResearchStatus,
  getResearchResult,
  getResearchQuestions,
  listResearchSessions,
  pollForCompletion,
  type ResearchStartRequest,
  type ResearchStatusResponse,
  type ResearchResultResponse,
  type ResearchQuestion,
  type SessionSummary,
  ResearchPhase,
} from './api-client';

// ============================================================================
// useResearchQuestions - Load pre-configured questions
// ============================================================================

export function useResearchQuestions() {
  const [questions, setQuestions] = useState<ResearchQuestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Only run on client side
    if (typeof window === 'undefined') return;
    
    async function loadQuestions() {
      try {
        setLoading(true);
        const data = await getResearchQuestions();
        setQuestions(data);
        setError(null);
      } catch (err) {
        console.error('Failed to load questions:', err);
        setError(err instanceof Error ? err.message : 'Failed to load questions');
      } finally {
        setLoading(false);
      }
    }

    loadQuestions();
  }, []);

  return { questions, loading, error };
}

// ============================================================================
// useResearchSession - Manage a single research session
// ============================================================================

interface UseResearchSessionOptions {
  pollInterval?: number;
  onProgress?: (status: ResearchStatusResponse) => void;
  onComplete?: (result: ResearchResultResponse) => void;
  onError?: (error: Error) => void;
}

export function useResearchSession(options: UseResearchSessionOptions = {}) {
  const {
    pollInterval = 3000,
    onProgress,
    onComplete,
    onError,
  } = options;

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [status, setStatus] = useState<ResearchStatusResponse | null>(null);
  const [result, setResult] = useState<ResearchResultResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isStarting, setIsStarting] = useState(false);

  const pollTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Start a new research session
  const start = useCallback(async (request: ResearchStartRequest) => {
    try {
      setIsStarting(true);
      setError(null);
      setResult(null);
      setStatus(null);

      const response = await startResearch(request);
      setSessionId(response.session_id);
      setIsStarting(false);

      // Start polling immediately
      pollStatus(response.session_id);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to start research');
      setError(error.message);
      setIsStarting(false);
      onError?.(error);
    }
  }, [onError]);

  // Poll for status updates
  const pollStatus = useCallback(async (sid: string) => {
    try {
      const statusData = await getResearchStatus(sid);
      setStatus(statusData);
      onProgress?.(statusData);

      if (statusData.phase === ResearchPhase.COMPLETED) {
        // Research completed - get final result
        const resultData = await getResearchResult(sid);
        setResult(resultData);
        onComplete?.(resultData);
      } else if (statusData.phase === ResearchPhase.FAILED) {
        // Research failed
        const errorMsg = statusData.error || 'Research failed';
        setError(errorMsg);
        onError?.(new Error(errorMsg));
      } else {
        // Continue polling
        pollTimeoutRef.current = setTimeout(() => {
          pollStatus(sid);
        }, pollInterval);
      }
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to get status');
      setError(error.message);
      onError?.(error);
    }
  }, [pollInterval, onProgress, onComplete, onError]);

  // Clean up polling on unmount
  useEffect(() => {
    return () => {
      if (pollTimeoutRef.current) {
        clearTimeout(pollTimeoutRef.current);
      }
    };
  }, []);

  // Reset the session
  const reset = useCallback(() => {
    if (pollTimeoutRef.current) {
      clearTimeout(pollTimeoutRef.current);
    }
    setSessionId(null);
    setStatus(null);
    setResult(null);
    setError(null);
  }, []);

  return {
    sessionId,
    status,
    result,
    error,
    isStarting,
    isRunning: status !== null && status.phase !== ResearchPhase.COMPLETED && status.phase !== ResearchPhase.FAILED,
    isCompleted: status?.phase === ResearchPhase.COMPLETED,
    isFailed: status?.phase === ResearchPhase.FAILED,
    progressPercentage: status?.progress_percentage || 0,
    currentAgent: status?.current_agent || null,
    start,
    reset,
  };
}

// ============================================================================
// useResearchWithPolling - Start research and automatically poll
// ============================================================================

export function useResearchWithPolling() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [status, setStatus] = useState<ResearchStatusResponse | null>(null);
  const [result, setResult] = useState<ResearchResultResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const startAndPoll = useCallback(async (request: ResearchStartRequest) => {
    try {
      setIsLoading(true);
      setError(null);
      setResult(null);
      setStatus(null);

      const finalResult = await pollForCompletion(
        (await startResearch(request)).session_id,
        (statusUpdate) => {
          setStatus(statusUpdate);
        }
      );

      setResult(finalResult);
      setSessionId(finalResult.session_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Research failed');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setSessionId(null);
    setStatus(null);
    setResult(null);
    setError(null);
  }, []);

  return {
    sessionId,
    status,
    result,
    error,
    isLoading,
    startAndPoll,
    reset,
  };
}

// ============================================================================
// useSessionsList - List active sessions
// ============================================================================

export function useSessionsList(conversationId?: string) {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      const data = await listResearchSessions(
        conversationId ? { conversation_id: conversationId } : undefined
      );
      setSessions(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sessions');
    } finally {
      setLoading(false);
    }
  }, [conversationId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { sessions, loading, error, refresh };
}

// ============================================================================
// useProgressMessages - Convert progress updates to chat messages
// ============================================================================

export interface ProgressMessage {
  id: string;
  text: string;
  timestamp: string;
  agent: string | null;
  isComplete: boolean;
}

export function useProgressMessages(status: ResearchStatusResponse | null) {
  const messages: ProgressMessage[] = [];

  if (status?.progress_updates) {
    status.progress_updates.forEach((update, index) => {
      messages.push({
        id: `progress-${index}`,
        text: update.message,
        timestamp: update.timestamp,
        agent: update.agent,
        isComplete: update.status === 'completed',
      });
    });
  }

  return messages;
}
