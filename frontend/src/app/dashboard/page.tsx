
"use client";

import { DocumentUpload } from "@/components/dashboard/document-upload";
import { RecentDocuments } from "@/components/dashboard/recent-documents";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleProcessDocument = async (file: File) => {
    setIsProcessing(true);
    setError(null);
    
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        router.push(`/dashboard/analysis?doc_id=${data.doc_id}`);
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.message || "Upload failed. Please try again.");
      }
    } catch (error) {
      console.error("Error uploading file:", error);
      setError("Network error. Please check your connection and try again.");
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
