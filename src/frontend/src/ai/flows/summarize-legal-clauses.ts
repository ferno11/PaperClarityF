'use server';

/**
 * @fileOverview Summarizes legal clauses extracted from a document.
 *
 * - summarizeLegalClause - A function that summarizes a given legal clause.
 * - SummarizeLegalClauseInput - The input type for the summarizeLegalClause function.
 * - SummarizeLegalClauseOutput - The return type for the summarizeLegalClause function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const SummarizeLegalClauseInputSchema = z.object({
  clauseText: z
    .string()
    .describe('The legal clause text to be summarized.'),
});
export type SummarizeLegalClauseInput = z.infer<typeof SummarizeLegalClauseInputSchema>;

const SummarizeLegalClauseOutputSchema = z.object({
  summary: z
    .string()
    .describe('The AI-generated summary of the legal clause.'),
});
export type SummarizeLegalClauseOutput = z.infer<typeof SummarizeLegalClauseOutputSchema>;

export async function summarizeLegalClause(input: SummarizeLegalClauseInput): Promise<SummarizeLegalClauseOutput> {
  return summarizeLegalClauseFlow(input);
}

const prompt = ai.definePrompt({
  name: 'summarizeLegalClausePrompt',
  input: {schema: SummarizeLegalClauseInputSchema},
  output: {schema: SummarizeLegalClauseOutputSchema},
  prompt: `You are a legal expert skilled at summarizing complex legal clauses into easy-to-understand summaries.  Please provide a concise summary of the following legal clause:\n\n{{{clauseText}}}`,
});

const summarizeLegalClauseFlow = ai.defineFlow(
  {
    name: 'summarizeLegalClauseFlow',
    inputSchema: SummarizeLegalClauseInputSchema,
    outputSchema: SummarizeLegalClauseOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
