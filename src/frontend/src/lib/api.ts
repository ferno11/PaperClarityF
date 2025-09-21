// API functions for communicating with the backend
// Default to port 9000 to match the backend `uvicorn.run(..., port=9000)` used
// in `src/backend/main.py` when running the server directly.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9000';

// Types for API responses
export interface UploadResponse {
  file_id: string;
  filename: string;
  message: string;
}

export interface AnalysisResponse {
  file_id: string;
  message: string;
  clauses_count: number;
}

export interface Clause {
  clause_id: string;
  original_text: string;
  summary: string;
  risk_level: 'High' | 'Medium' | 'Low';
  word_count?: number;
  entities?: string[];
}

export interface RiskSummary {
  High: number;
  Medium: number;
  Low: number;
}

export interface ResultsResponse {
  file_id: string;
  filename: string;
  clauses: Clause[];
  risk_summary: RiskSummary;
  total_clauses: number;
  status: string;
  analysis_time?: string;
}

export interface ChatResponse {
  answer: string;
  relevant_clauses: string[];
}

// API functions
export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  
  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Upload failed: ${response.status}`);
  }
  
  return response.json();
}

export async function analyzeDocument(fileId: string): Promise<AnalysisResponse> {
  const response = await fetch(`${API_BASE_URL}/api/analyze/${fileId}`, {
    method: "POST",
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Analysis failed: ${response.status}`);
  }
  
  return response.json();
}

export async function fetchResults(fileId: string): Promise<ResultsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/results/${fileId}`);
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch results: ${response.status}`);
  }
  
  return response.json();
}

export async function chatWithDoc(fileId: string, question: string): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat/${fileId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Chat failed: ${response.status}`);
  }
  
  return response.json();
}

// Legacy API functions for backward compatibility
export async function getClauses(docId: string): Promise<ResultsResponse> {
  return fetchResults(docId);
}

export async function askQuestion(docId: string, question: string): Promise<ChatResponse> {
  return chatWithDoc(docId, question);
}
