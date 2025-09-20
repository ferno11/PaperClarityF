
"use client";

import { FileUp } from "lucide-react";
import { Button } from "../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { useRef, useState } from "react";

type DocumentUploadProps = {
  onProcessDocument: (file: File) => void;
};

export function DocumentUpload({ onProcessDocument }: DocumentUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFile(event.target.files[0]);
    }
  };

  const handleUploadClick = () => {
    if (file) {
      onProcessDocument(file);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Start New Analysis</CardTitle>
        <CardDescription>Upload a legal document to get started.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-muted-foreground/30 bg-background p-8 text-center sm:p-12">
          <div className="mb-4 rounded-full border-8 border-muted bg-card p-4">
            <FileUp className="h-10 w-10 text-primary" />
          </div>
          <h3 className="mb-2 text-xl font-semibold sm:text-2xl">
            Upload Your Legal Document
          </h3>
          <p className="mb-6 max-w-sm text-sm text-muted-foreground sm:text-base">
            Drag and drop a file here, or click to select a file.
          </p>
          <div className="flex flex-col items-center gap-4">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              className="hidden"
            />
            <Button onClick={() => fileInputRef.current?.click()} size="lg">
              Select Document
            </Button>
            {file && (
              <Button onClick={handleUploadClick} size="lg">
                Upload and Process
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
