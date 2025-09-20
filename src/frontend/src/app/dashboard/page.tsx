
"use client";

import { DocumentUpload } from "@/components/dashboard/document-upload";
import { RecentDocuments } from "@/components/dashboard/recent-documents";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";
import { uploadDocument, analyzeDocument } from "@/lib/api";

export default function DashboardPage() {
  const router = useRouter();
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleProcessDocument = async (file: File) => {
    setIsProcessing(true);
    setError(null);

    try {
      // Step 1: Upload the document
      const uploadResponse = await uploadDocument(file);
      console.log("Upload successful:", uploadResponse);

      // Step 2: Analyze the document
      const analysisResponse = await analyzeDocument(uploadResponse.file_id);
      console.log("Analysis successful:", analysisResponse);

      // Step 3: Navigate to analysis page with file_id
      router.push(`/dashboard/analysis?file_id=${uploadResponse.file_id}`);
    } catch (error) {
      console.error("Error processing document:", error);
      setError(error instanceof Error ? error.message : "Failed to process document. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="container mx-auto max-w-5xl py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Dashboard</h1>
        <p className="text-muted-foreground">
          Upload a new document or review a recent analysis.
        </p>
      </div>
      
      {error && (
        <Alert className="mb-6" variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      <div className="grid grid-cols-1 gap-8">
        <DocumentUpload 
          onProcessDocument={handleProcessDocument} 
          isProcessing={isProcessing}
        />
        <RecentDocuments />
      </div>
    </div>
  );
}
