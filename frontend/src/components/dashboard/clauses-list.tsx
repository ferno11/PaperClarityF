import type { Clause } from "@/lib/types";
import { Accordion } from "@/components/ui/accordion";
import { ClauseCard } from "./clause-card";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

type ClausesListProps = {
  clauses: Clause[];
};

export function ClausesList({ clauses }: ClausesListProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Analyzed Clauses</CardTitle>
        <CardDescription>
          Found {clauses.length} clauses in your document. Review each one below.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Accordion type="single" collapsible className="w-full">
          {clauses.map((clause) => (
            <ClauseCard key={clause.clause_id} clause={clause} />
          ))}
        </Accordion>
      </CardContent>
    </Card>
  );
}
