
"use client";

import { FileUp, Upload, AlertCircle, CheckCircle2, Loader2 } from "lucide-react";
import { Button } from "../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Alert, AlertDescription } from "../ui/alert";
import { useRef, useState, useCallback } from "react";
import { cn } from "@/lib/utils";

type DocumentUploadProps = {
  onProcessDocument: (file: File) => Promise<void>;
  isProcessing?: boolean;
};

const ACCEPTED_FILE_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'application/msword': ['.doc'],
};

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export function DocumentUpload({ onProcessDocument, isProcessing = false }: DocumentUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): string | null => {
    if (file.size > MAX_FILE_SIZE) {
      return "File size must be less than 10MB";
    }
    
    const fileType = file.type;
    if (!Object.keys(ACCEPTED_FILE_TYPES).includes(fileType)) {
      return "Please upload a PDF or Word document (.pdf, .doc, .docx)";
    }
    
    return null;
  };

  const handleFileChange = (selectedFile: File) => {
    setError(null);
    const validationError = validateFile(selectedFile);
    
    if (validationError) {
      setError(validationError);
      setFile(null);
      return;
    }
    
    setFile(selectedFile);
  };

  const handleFileInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      handleFileChange(event.target.files[0]);
    }
  };

  const handleUploadClick = async () => {
    if (file && !isProcessing) {
      try {
        await onProcessDocument(file);
      } catch (error) {
        setError("Failed to process document. Please try again.");
      }
    }
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  }, []);

  const resetUpload = () => {
    setFile(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileUp className="h-5 w-5" />
          Start New Analysis
        </CardTitle>
        <CardDescription>
          Upload a legal document to analyze clauses and assess risks.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div
          className={cn(
            "flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 text-center transition-colors",
            dragActive
              ? "border-primary bg-primary/5"
              : "border-muted-foreground/30 bg-background",
            error && "border-destructive bg-destructive/5"
          )}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          role="button"
          tabIndex={0}
          aria-label="File upload area. Drag and drop a file here or click to select."
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              fileInputRef.current?.click();
            }
          }}
        >
          <div className="mb-4 rounded-full border-8 border-muted bg-card p-4">
            {isProcessing ? (
              <Loader2 className="h-10 w-10 text-primary animate-spin" />
            ) : (
              <FileUp className="h-10 w-10 text-primary" />
            )}
          </div>
          
          <h3 className="mb-2 text-xl font-semibold sm:text-2xl">
            {isProcessing ? "Processing Document..." : "Upload Your Legal Document"}
          </h3>
          
          <p className="mb-6 max-w-sm text-sm text-muted-foreground sm:text-base">
            {isProcessing 
              ? "Please wait while we analyze your document..."
              : "Drag and drop a file here, or click to select a file."
            }
          </p>

          {error && (
            <Alert className="mb-4 max-w-sm">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {file && !isProcessing && (
            <div className="mb-4 flex items-center gap-2 rounded-lg bg-muted p-3">
              <CheckCircle2 className="h-4 w-4 text-green-500" />
              <span className="text-sm font-medium">{file.name}</span>
              <span className="text-xs text-muted-foreground">
                ({(file.size / 1024 / 1024).toFixed(2)} MB)
              </span>
            </div>
          )}

          <div className="flex flex-col items-center gap-4">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileInputChange}
              accept=".pdf,.doc,.docx"
              className="hidden"
              disabled={isProcessing}
            />
            
            {!file ? (
              <Button 
                onClick={() => fileInputRef.current?.click()} 
                size="lg"
                disabled={isProcessing}
              >
                <Upload className="h-4 w-4 mr-2" />
                Select Document
              </Button>
            ) : (
              <div className="flex gap-2">
                <Button 
                  onClick={handleUploadClick} 
                  size="lg"
                  disabled={isProcessing}
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Upload className="h-4 w-4 mr-2" />
                      Upload and Process
                    </>
                  )}
                </Button>
                <Button 
                  onClick={resetUpload} 
                  variant="outline"
                  disabled={isProcessing}
                >
                  Cancel
                </Button>
              </div>
            )}
          </div>

          <p className="mt-4 text-xs text-muted-foreground">
            Supported formats: PDF, DOC, DOCX (max 10MB)
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
