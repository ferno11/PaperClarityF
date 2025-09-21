
"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { RiskOverview } from "@/components/dashboard/risk-overview";
import { ClausesList } from "@/components/dashboard/clauses-list";
import { ChatPanel } from "@/components/dashboard/chat-panel";
import { Disclaimer } from "@/components/dashboard/disclaimer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, FileText, Loader2 } from "lucide-react";
import type { Clause, ChatMessage } from "@/lib/types";
import { fetchResults, chatWithDoc } from "@/lib/api";

function AnalysisPageContent() {
  const searchParams = useSearchParams();
  const fileId = searchParams.get("file_id") || searchParams.get("doc_id");

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [documentText, setDocumentText] = useState("");
  const [clauses, setClauses] = useState<Clause[]>([]);
  const [analysisSummary, setAnalysisSummary] = useState("");
  const [filename, setFilename] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (fileId) {
      const fetchAnalysis = async () => {
        setLoading(true);
        setError(null);
        
        try {
          const data = await fetchResults(fileId);
          setFilename(data.filename || "Document");
          setClauses(data.clauses || []);
          
          const riskSummary = data.risk_summary || { High: 0, Medium: 0, Low: 0 };
          setAnalysisSummary(
            `Document processed successfully. Found ${data.total_clauses || 0} clauses with risk distribution: ` +
            `High: ${riskSummary.High}, Medium: ${riskSummary.Medium}, Low: ${riskSummary.Low}`
          );
          
          // Combine all clause text for document preview
          const fullText = (data.clauses || []).map((clause: any) => 
            `${clause.clause_id}: ${clause.original_text}`
          ).join('\n\n');
          setDocumentText(fullText);
        } catch (error) {
          console.error("Error fetching analysis:", error);
          setError(error instanceof Error ? error.message : "Network error. Please check your connection and try again.");
        } finally {
          setLoading(false);
        }
      };
      fetchAnalysis();
    } else {
      setError("No document ID provided.");
      setLoading(false);
    }
  }, [fileId]);

  const handleSendMessage = async (input: string) => {
    if (!fileId) return;

    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: "user",
      content: input,
    };
    setMessages((prev) => [...prev, userMessage]);

    // Use a stable id for the assistant typing placeholder so we can
    // replace it reliably with the final assistant message when the
    // API returns. Previously we generated a new timestamp twice which
    // made replacement fail.
    const typingId = `msg-${Date.now()}`;
    const assistantTypingMessage: ChatMessage = {
      id: typingId,
      role: "assistant",
      content: "...",
    };
    setMessages((prev) => [...prev, assistantTypingMessage]);

    try {
      const result = await chatWithDoc(fileId, input);
      const assistantMessage: ChatMessage = {
        id: typingId, // same id so we replace the placeholder
        role: "assistant",
        content: result.answer,
        references: result.relevant_clauses,
      };
      setMessages((prev) => prev.map((msg) => (msg.id === typingId ? assistantMessage : msg)));
    } catch (error) {
      console.error("Error sending message:", error);
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

  if (loading) {
    return (
      <div className="flex-1 items-start grid grid-cols-1 lg:grid-cols-12 gap-6 p-4 md:p-6">
        <div className="hidden lg:block lg:col-span-5 xl:col-span-4">
          <Card className="sticky top-20">
            <CardHeader>
              <CardTitle>Document Preview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
              </div>
            </CardContent>
          </Card>
        </div>

        <main className="lg:col-span-4 xl:col-span-5 space-y-6 pb-6">
          <Card>
            <CardHeader>
              <CardTitle>Analysis Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Risk Assessment</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="md:col-span-2 space-y-4">
                <Skeleton className="h-32 w-full" />
                <Skeleton className="h-32 w-full" />
              </div>
              <div className="md:col-span-1">
                <Skeleton className="h-64 w-full" />
              </div>
            </CardContent>
          </Card>
        </main>

        <aside className="sticky top-20 hidden md:block lg:col-span-3 xl:col-span-3">
          <Card>
            <CardHeader>
              <CardTitle>Ask Your Document</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
              </div>
            </CardContent>
          </Card>
        </aside>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-destructive" />
              Analysis Error
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile Chat Panel - Always visible on mobile */}
      <div className="block md:hidden p-4">
        <ChatPanel messages={messages} onSendMessage={handleSendMessage} onReset={handleReset} />
      </div>

      <div className="flex-1 items-start grid grid-cols-1 lg:grid-cols-12 gap-6 p-4 md:p-6">
        {/* Document Preview - Hidden on mobile, visible on desktop */}
        <div className="hidden lg:block lg:col-span-5 xl:col-span-4">
          <Card className="sticky top-20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Document Preview
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[calc(100vh-12rem)]">
                <pre className="text-sm text-muted-foreground whitespace-pre-wrap p-4 bg-muted/50 rounded-md font-sans">
                  {documentText || "No document content available."}
                </pre>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <main className="lg:col-span-4 xl:col-span-5 space-y-6 pb-6">
          {/* Analysis Summary */}
          <Card>
            <CardHeader>
              <CardTitle>Analysis Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">{analysisSummary}</p>
            </CardContent>
          </Card>

          {/* Risk Assessment */}
          <Card>
            <CardHeader>
              <CardTitle>Risk Assessment</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <ClausesList clauses={clauses} />
              </div>
              <div className="lg:col-span-1">
                <RiskOverview clauses={clauses} />
              </div>
            </CardContent>
          </Card>

          {/* Disclaimers */}
          <Disclaimer />
        </main>

        {/* Desktop Chat Panel */}
        <aside className="sticky top-20 hidden md:block lg:col-span-3 xl:col-span-3">
          <ChatPanel messages={messages} onSendMessage={handleSendMessage} onReset={handleReset} />
        </aside>
      </div>
    </div>
  );
}

export default function AnalysisPage() {
  return (
    <Suspense fallback={
      <div className="flex-1 flex items-center justify-center p-8">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Loading Analysis...</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
            </div>
          </CardContent>
        </Card>
      </div>
    }>
      <AnalysisPageContent />
    </Suspense>
  );
}
