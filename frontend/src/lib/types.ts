export type Clause = {
  clause_id: string;
  original_text: string;
  summary: string;
  risk_level: 'High' | 'Medium' | 'Low' | 'Unknown';
  entities?: string[];
  word_count?: number;
};

export type ChatMessage = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  references?: string[];
};
