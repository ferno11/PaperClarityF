import { AlertTriangle, Shield, Trash2 } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

export function Disclaimer() {
  return (
    <div className="space-y-4">
      <Alert className="border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-950">
        <AlertTriangle className="h-4 w-4 text-amber-600 dark:text-amber-400" />
        <AlertDescription className="text-amber-800 dark:text-amber-200">
          <strong>Important Disclaimer:</strong> This tool provides AI-generated summaries and risk assessments for informational purposes only. 
          It does not constitute legal advice, and you should consult with a qualified attorney for any legal matters.
        </AlertDescription>
      </Alert>
      
      <Alert className="border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950">
        <Shield className="h-4 w-4 text-blue-600 dark:text-blue-400" />
        <AlertDescription className="text-blue-800 dark:text-blue-200">
          <strong>Privacy & Security:</strong> Your uploaded documents are processed securely and automatically deleted after analysis. 
          No data is stored permanently on our servers.
        </AlertDescription>
      </Alert>
    </div>
  );
}
