/**
 * API Client for Trend Research Backend
 * 
 * This module provides type-safe functions to interact with the FastAPI backend.
 * All functions handle errors and return consistent response structures.
 */

// ============================================================================
// TypeScript Types
// ============================================================================

export enum ResearchPhase {
  PENDING = "pending",
  DATA_COLLECTION = "data_collection",
  ANALYSIS = "analysis",
  REPORT_GENERATION = "report_generation",
  COMPLETED = "completed",
  FAILED = "failed"
}

export enum AgentStatus {
  RUNNING = "running",
  COMPLETED = "completed",
  FAILED = "failed"
}

export interface ResearchQuestion {
  id: string;
  title: string;
  question: string;
  focus: string;
  search_terms: string[];
}

export interface ResearchStartRequest {
  question?: string;
  search_query?: string;
  question_id?: string;
  conversation_id?: string;
  max_results?: number;
}

export interface ResearchStartResponse {
  session_id: string;
  message: string;
  question: string;
  search_query: string;
  status_url: string;
  result_url: string;
}

export interface ProgressUpdate {
  timestamp: string;
  phase: ResearchPhase;
  agent: string | null;
  status: AgentStatus;
  message: string;
  data?: Record<string, any> | null;
}

export interface ResearchStatusResponse {
  session_id: string;
  phase: ResearchPhase;
  progress_percentage: number;
  current_agent: string | null;
  progress_updates: ProgressUpdate[];
  started_at: string;
  estimated_completion: string | null;
  error?: string | null;
}

export interface DataCollected {
  social_media: {
    twitter: { total_results: number };
    tiktok: { total_results: number };
    reddit: { total_results: number };
  };
  trends: {
    search_volume_index: number;
    trending_status: string;
  };
  web_intelligence: {
    total_results: number;
  };
}

export interface ResearchResultResponse {
  session_id: string;
  question: string;
  search_query: string;
  phase: ResearchPhase;
  started_at: string;
  completed_at: string;
  execution_time_seconds: number;
  data_collected: DataCollected;
  total_data_points: number;
  failed_apis: string[];
  insights: string;
  report: string;
  executive_summary: string | null;
  key_findings: string[] | null;
  recommendations: string[] | null;
  progress_updates: ProgressUpdate[];
}

export interface SessionSummary {
  session_id: string;
  question: string;
  search_query: string;
  conversation_id: string | null;
  phase: ResearchPhase;
  created_at: string;
  updated_at: string;
  progress_count: number;
  has_result: boolean;
}

export interface SessionStatistics {
  total_sessions: number;
  max_sessions: number;
  by_phase: Record<string, number>;
  capacity_percentage: number;
}

export interface ApiError {
  error: string;
  status_code: number;
  timestamp: string;
}

// ============================================================================
// Configuration
// ============================================================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Generic fetch wrapper with error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: response.statusText,
        status_code: response.status,
        timestamp: new Date().toISOString(),
      }));
      throw new Error(errorData.error || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
}

// ============================================================================
// API Functions
// ============================================================================

/**
 * Start a new research session
 * 
 * @param request - Research request parameters
 * @returns Promise with session details
 * 
 * @example
 * // Using pre-configured question
 * const result = await startResearch({
 *   question_id: "gen_z_nigeria",
 *   conversation_id: "conv-123"
 * });
 * 
 * @example
 * // Using custom question
 * const result = await startResearch({
 *   question: "What are AI trends?",
 *   search_query: "AI trends 2024",
 *   conversation_id: "conv-123"
 * });
 */
export async function startResearch(
  request: ResearchStartRequest
): Promise<ResearchStartResponse> {
  return apiFetch<ResearchStartResponse>("/api/research/start", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

/**
 * Get the current status of a research session
 * 
 * Use this to poll for progress updates during research execution.
 * Recommended polling interval: 2-3 seconds.
 * 
 * @param sessionId - The session ID returned from startResearch()
 * @returns Promise with current status and progress
 * 
 * @example
 * const status = await getResearchStatus(sessionId);
 * console.log(`Progress: ${status.progress_percentage}%`);
 * console.log(`Phase: ${status.phase}`);
 */
export async function getResearchStatus(
  sessionId: string
): Promise<ResearchStatusResponse> {
  return apiFetch<ResearchStatusResponse>(
    `/api/research/${sessionId}/status`
  );
}

/**
 * Get the final result of a completed research session
 * 
 * Only call this after status shows phase === "completed".
 * Returns the full research report with all data.
 * 
 * @param sessionId - The session ID
 * @returns Promise with complete research results
 * 
 * @example
 * const result = await getResearchResult(sessionId);
 * console.log(result.executive_summary);
 * console.log(result.key_findings);
 */
export async function getResearchResult(
  sessionId: string
): Promise<ResearchResultResponse> {
  return apiFetch<ResearchResultResponse>(
    `/api/research/${sessionId}/result`
  );
}

/**
 * Get list of pre-configured research questions
 * 
 * These questions are ready-to-use templates with optimized search terms.
 * Use the 'id' field with startResearch() to use these questions.
 * 
 * @returns Promise with array of research questions
 * 
 * @example
 * const questions = await getResearchQuestions();
 * questions.forEach(q => console.log(q.title));
 */
export async function getResearchQuestions(): Promise<ResearchQuestion[]> {
  return apiFetch<ResearchQuestion[]>("/api/research/questions");
}

/**
 * List active research sessions
 * 
 * @param filters - Optional filters for conversation_id or phase
 * @returns Promise with array of session summaries
 * 
 * @example
 * // Get all sessions
 * const sessions = await listResearchSessions();
 * 
 * @example
 * // Get sessions for a specific conversation
 * const sessions = await listResearchSessions({
 *   conversation_id: "conv-123"
 * });
 */
export async function listResearchSessions(filters?: {
  conversation_id?: string;
  phase?: ResearchPhase;
}): Promise<SessionSummary[]> {
  const params = new URLSearchParams();
  if (filters?.conversation_id) {
    params.append("conversation_id", filters.conversation_id);
  }
  if (filters?.phase) {
    params.append("phase", filters.phase);
  }

  const queryString = params.toString();
  const endpoint = `/api/research/sessions${queryString ? `?${queryString}` : ""}`;

  return apiFetch<SessionSummary[]>(endpoint);
}

/**
 * Delete a research session
 * 
 * This will cancel any running research task and free up capacity.
 * 
 * @param sessionId - The session ID to delete
 * @returns Promise with success message
 * 
 * @example
 * await deleteResearchSession(sessionId);
 */
export async function deleteResearchSession(
  sessionId: string
): Promise<{ message: string }> {
  return apiFetch<{ message: string }>(`/api/research/${sessionId}`, {
    method: "DELETE",
  });
}

/**
 * Get server statistics
 * 
 * Returns information about active sessions, capacity, and usage.
 * Useful for monitoring and debugging.
 * 
 * @returns Promise with server statistics
 * 
 * @example
 * const stats = await getSessionStatistics();
 * console.log(`Active: ${stats.total_sessions}/${stats.max_sessions}`);
 */
export async function getSessionStatistics(): Promise<SessionStatistics> {
  return apiFetch<SessionStatistics>("/api/research/statistics");
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Poll for research completion
 * 
 * Helper function that polls the status endpoint until research completes.
 * Calls onProgress callback with each status update.
 * 
 * @param sessionId - The session ID to monitor
 * @param onProgress - Callback function called with each status update
 * @param pollInterval - Polling interval in milliseconds (default: 3000)
 * @returns Promise that resolves with final result when complete
 * 
 * @example
 * const result = await pollForCompletion(
 *   sessionId,
 *   (status) => {
 *     console.log(`Progress: ${status.progress_percentage}%`);
 *   }
 * );
 */
export async function pollForCompletion(
  sessionId: string,
  onProgress: (status: ResearchStatusResponse) => void,
  pollInterval: number = 3000
): Promise<ResearchResultResponse> {
  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        const status = await getResearchStatus(sessionId);
        onProgress(status);

        if (status.phase === ResearchPhase.COMPLETED) {
          const result = await getResearchResult(sessionId);
          resolve(result);
        } else if (status.phase === ResearchPhase.FAILED) {
          reject(new Error(status.error || "Research failed"));
        } else {
          // Continue polling
          setTimeout(poll, pollInterval);
        }
      } catch (error) {
        reject(error);
      }
    };

    poll();
  });
}

/**
 * Start research and wait for completion
 * 
 * Convenience function that combines startResearch() and pollForCompletion().
 * 
 * @param request - Research request parameters
 * @param onProgress - Callback function for progress updates
 * @returns Promise with final result
 * 
 * @example
 * const result = await startAndWaitForResearch(
 *   { question_id: "gen_z_nigeria" },
 *   (status) => {
 *     updateUI(status.progress_percentage);
 *   }
 * );
 */
export async function startAndWaitForResearch(
  request: ResearchStartRequest,
  onProgress: (status: ResearchStatusResponse) => void
): Promise<ResearchResultResponse> {
  const { session_id } = await startResearch(request);
  return pollForCompletion(session_id, onProgress);
}

/**
 * Check if backend is healthy
 * 
 * @returns Promise with health status
 */
export async function checkHealth(): Promise<{
  status: string;
  services: Record<string, string>;
}> {
  return apiFetch<any>("/health");
}

// ============================================================================
// Chat API Types
// ============================================================================

export enum ChatAction {
  RESPOND = "respond",
  RESEARCH = "research",
  CLARIFY = "clarify"
}

export interface ChatRequest {
  message: string;
  conversation_id: string;
}

export interface ChatResponse {
  action: ChatAction;
  message: string;
  research_question: string | null;
  search_query: string | null;
  timestamp: string;
}

// ============================================================================
// Chat API Functions
// ============================================================================

/**
 * Send a chat message to the AI assistant
 * 
 * The AI will analyze the message and return one of three actions:
 * - "respond": Normal conversational response
 * - "research": User wants trend research (includes research_question and search_query)
 * - "clarify": User's request is unclear, AI asks for clarification
 * 
 * @param request - Chat message and conversation ID
 * @returns Promise with AI response and action
 * 
 * @example
 * const response = await sendChatMessage({
 *   message: "Hi there!",
 *   conversation_id: "conv-123"
 * });
 * 
 * if (response.action === ChatAction.RESEARCH) {
 *   // Start research with response.research_question and response.search_query
 * }
 */
export async function sendChatMessage(
  request: ChatRequest
): Promise<ChatResponse> {
  return apiFetch<ChatResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

/**
 * Clear chat history for a conversation
 * 
 * @param conversationId - The conversation to clear
 * @returns Promise with success status
 */
export async function clearChatHistory(
  conversationId: string
): Promise<{ success: boolean; message: string }> {
  return apiFetch<{ success: boolean; message: string }>(
    `/api/chat/${conversationId}`,
    { method: "DELETE" }
  );
}

/**
 * Check chat service health
 * 
 * @returns Promise with chat service status
 */
export async function checkChatHealth(): Promise<{
  status: string;
  llm_available: boolean;
  active_conversations: number;
}> {
  return apiFetch<any>("/api/chat/health");
}
