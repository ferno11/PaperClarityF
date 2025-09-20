
"use client";

import { DocumentUpload } from "@/components/dashboard/document-upload";
import { RecentDocuments } from "@/components/dashboard/recent-documents";
import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const router = useRouter();

  const handleProcessDocument = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        router.push(`/dashboard/analysis?file_id=${data.file_id}`);
      } else {
        console.error("Upload failed");
      }
    } catch (error) {
      console.error("Error uploading file:", error);
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
      <div className="grid grid-cols-1 gap-8">
        <DocumentUpload onProcessDocument={handleProcessDocument} />
        <RecentDocuments />
      </div>
    </div>
  );
}
