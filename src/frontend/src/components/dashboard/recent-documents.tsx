import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "../ui/button";

const recentDocs = [
    { id: 1, name: "Non-Disclosure Agreement.pdf", date: "2024-07-22", risk: "Medium" },
    { id: 2, name: "Master Service Agreement.docx", date: "2024-07-21", risk: "High" },
    { id: 3, name: "Employment Contract.pdf", date: "2024-07-20", risk: "Low" },
]

export function RecentDocuments() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Analyses</CardTitle>
        <CardDescription>
          Review your previously analyzed documents.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Accordion type="single" collapsible defaultValue="item-1">
            <AccordionItem value="item-1">
                <AccordionTrigger className="text-lg font-semibold">View Recent Documents</AccordionTrigger>
                <AccordionContent>
                    <ul className="space-y-4">
                        {recentDocs.map(doc => (
                            <li key={doc.id} className="flex items-center justify-between p-2 rounded-md hover:bg-muted">
                                <div>
                                    <p className="font-medium">{doc.name}</p>
                                    <p className="text-sm text-muted-foreground">Analyzed on: {doc.date}</p>
                                </div>
                                <div className="flex items-center gap-4">
                                     <p className="text-sm">Risk Level: <span className={`font-semibold ${doc.risk === 'High' ? 'text-red-500' : doc.risk === 'Medium' ? 'text-yellow-500' : 'text-green-500'}`}>{doc.risk}</span></p>
                                    <Button variant="outline" size="sm">View Analysis</Button>
                                </div>
                            </li>
                        ))}
                    </ul>
                </AccordionContent>
            </AccordionItem>
        </Accordion>
      </CardContent>
    </Card>
  );
}
