
"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { RiskOverview } from "@/components/dashboard/risk-overview";
import { ClausesList } from "@/components/dashboard/clauses-list";
import { ChatPanel } from "@/components/dashboard/chat-panel";
import { Disclaimer } from "@/components/dashboard/disclaimer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { Clause, ChatMessage } from "@/lib/types";

export default function AnalysisPage() {
  const searchParams = useSearchParams();
  const docId = searchParams.get("doc_id");

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [documentText, setDocumentText] = useState("");
  const [clauses, setClauses] = useState<Clause[]>([]);
  const [analysisSummary, setAnalysisSummary] = useState("");
  const [filename, setFilename] = useState("");

  useEffect(() => {
    if (docId) {
      const fetchAnalysis = async () => {
        try {
          const response = await fetch(`http://localhost:8000/clauses/${docId}`);
          if (response.ok) {
            const data = await response.json();
            setFilename(data.filename || "Document");
            setClauses(data.clauses || []);
            setAnalysisSummary(`Document processed successfully. Found ${data.total_clauses} clauses with risk distribution: High: ${data.risk_summary.High}, Medium: ${data.risk_summary.Medium}, Low: ${data.risk_summary.Low}`);
            
            // Combine all clause text for document preview
            const fullText = data.clauses.map((clause: any) => 
              `${clause.clause_id}: ${clause.original_text}`
            ).join('\n\n');
            setDocumentText(fullText);
          } else {
            console.error("Failed to fetch analysis");
          }
        } catch (error) {
          console.error("Error fetching analysis:", error);
        }
      };
      fetchAnalysis();
    }
  }, [docId]);

  const handleSendMessage = async (input: string) => {
    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: "user",
      content: input,
    };
    setMessages((prev) => [...prev, userMessage]);

    const assistantTypingMessage: ChatMessage = {
      id: `msg-${Date.now() + 1}`,
      role: "assistant",
      content: "...",
    };
    setMessages((prev) => [...prev, assistantTypingMessage]);

    try {
      const response = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ doc_id: docId, question: input }),
      });

      if (response.ok) {
        const result = await response.json();
        const assistantMessage: ChatMessage = {
          id: `msg-${Date.now() + 1}`,
          role: "assistant",
          content: result.answer,
          references: result.relevant_clauses,
        };
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessage.id ? assistantMessage : msg
          )
        );
      } else {
        const errorMessage: ChatMessage = {
          id: `msg-${Date.now() + 1}`,
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
        };
        setMessages((prev) =>
          prev.map((msg) => (msg.id === errorMessage.id ? errorMessage : msg))
        );
      }
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
      };
      setMessages((prev) =>
        prev.map((msg) => (msg.id === errorMessage.id ? errorMessage : msg))
      );
    }
  };

  const handleReset = () => {
    setMessages([]);
  }

  return (
    <div className="flex-1 items-start grid grid-cols-1 lg:grid-cols-12 gap-6 p-4 md:p-6">
      <div className="hidden lg:block lg:col-span-5 xl:col-span-4">
        <Card className="sticky top-20">
          <CardHeader>
            <CardTitle>Document Preview</CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[calc(100vh-12rem)]">
              <pre className="text-sm text-muted-foreground whitespace-pre-wrap p-4 bg-muted/50 rounded-md font-sans">
                {documentText}
              </pre>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      <main className="lg:col-span-4 xl:col-span-5 space-y-6 pb-6">
        <Card>
          <CardHeader>
            <CardTitle>Analysis Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">{analysisSummary}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Risk Assessment</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2">
              <ClausesList clauses={clauses} />
            </div>
            <div className="md:col-span-1">
              <RiskOverview clauses={clauses} />
            </div>
          </CardContent>
        </Card>

        <Disclaimer />
      </main>

      <aside className="sticky top-20 hidden md:block lg:col-span-3 xl:col-span-3">
        <ChatPanel messages={messages} onSendMessage={handleSendMessage} onReset={handleReset} />
      </aside>
    </div>
  );
}
