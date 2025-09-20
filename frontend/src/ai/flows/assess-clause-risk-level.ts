'use server';

/**
 * @fileOverview Assesses the risk level of a given clause (High, Medium, Low).
 *
 * - assessClauseRiskLevel - A function that assesses the risk level of a clause.
 * - AssessClauseRiskLevelInput - The input type for the assessClauseRiskLevel function.
 * - AssessClauseRiskLevelOutput - The return type for the assessClauseRiskLevel function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const AssessClauseRiskLevelInputSchema = z.object({
  clauseText: z.string().describe('The text of the legal clause to assess.'),
  documentContext: z
    .string()
    .optional()
    .describe(
      'Additional context about the legal document to help assess the risk.'
    ),
});
export type AssessClauseRiskLevelInput = z.infer<
  typeof AssessClauseRiskLevelInputSchema
>;

const AssessClauseRiskLevelOutputSchema = z.object({
  riskLevel: z.enum(['High', 'Medium', 'Low']).describe('The risk level of the clause.'),
  explanation: z
    .string()
    .describe('Explanation of why the clause was assigned the given risk level.'),
});
export type AssessClauseRiskLevelOutput = z.infer<
  typeof AssessClauseRiskLevelOutputSchema
>;

export async function assessClauseRiskLevel(
  input: AssessClauseRiskLevelInput
): Promise<AssessClauseRiskLevelOutput> {
  return assessClauseRiskLevelFlow(input);
}

const prompt = ai.definePrompt({
  name: 'assessClauseRiskLevelPrompt',
  input: {schema: AssessClauseRiskLevelInputSchema},
  output: {schema: AssessClauseRiskLevelOutputSchema},
  prompt: `You are an expert legal risk assessor.

You are assessing the risk level of individual clauses within legal documents. Consider the clause text and any provided document context to determine the risk level.

Respond with a risk level of "High", "Medium", or "Low", and provide a brief explanation for your assessment.

Clause Text: {{{clauseText}}}
Document Context: {{{documentContext}}}

Risk Level: <riskLevel>
Explanation: <explanation>`,
});

const assessClauseRiskLevelFlow = ai.defineFlow(
  {
    name: 'assessClauseRiskLevelFlow',
    inputSchema: AssessClauseRiskLevelInputSchema,
    outputSchema: AssessClauseRiskLevelOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
