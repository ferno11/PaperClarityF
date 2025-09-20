export type Clause = {
  id: string;
  originalText: string;
  summary: string;
  riskLevel: 'High' | 'Medium' | 'Low' | 'Unknown';
  explanation: string;
};

export type ChatMessage = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  references?: string[];
};
