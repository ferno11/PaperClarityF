import { config } from 'dotenv';
config();

import '@/ai/flows/assess-clause-risk-level.ts';
import '@/ai/flows/answer-document-questions.ts';
import '@/ai/flows/summarize-legal-clauses.ts';