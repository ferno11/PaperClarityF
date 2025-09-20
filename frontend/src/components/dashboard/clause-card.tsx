import type { Clause } from "@/lib/types";
import {
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { 
  ShieldAlert, 
  ShieldCheck, 
  ShieldQuestion, 
  ShieldX, 
  ChevronDown, 
  ChevronRight,
  Copy,
  ExternalLink,
  FileText
} from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

type ClauseCardProps = {
  clause: Clause;
};

const riskConfig = {
  High: {
    label: "High Risk",
    icon: ShieldAlert,
    className: "bg-red-500/10 text-red-700 border-red-500/20 hover:bg-red-500/20 dark:text-red-400",
    badgeClassName: "bg-red-100 text-red-800 border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800",
    priority: 1,
  },
  Medium: {
    label: "Medium Risk",
    icon: ShieldQuestion,
    className: "bg-yellow-500/10 text-yellow-700 border-yellow-500/20 hover:bg-yellow-500/20 dark:text-yellow-400",
    badgeClassName: "bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-400 dark:border-yellow-800",
    priority: 2,
  },
  Low: {
    label: "Low Risk",
    icon: ShieldCheck,
    className: "bg-green-500/10 text-green-700 border-green-500/20 hover:bg-green-500/20 dark:text-green-400",
    badgeClassName: "bg-green-100 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800",
    priority: 3,
  },
  Unknown: {
    label: "Unknown",
    icon: ShieldX,
    className: "bg-gray-500/10 text-gray-700 border-gray-500/20 hover:bg-gray-500/20 dark:text-gray-400",
    badgeClassName: "bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-900/20 dark:text-gray-400 dark:border-gray-800",
    priority: 4,
  }
};

export function ClauseCard({ clause }: ClauseCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  const config = riskConfig[clause.risk_level] || riskConfig.Unknown;
  const Icon = config.icon;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(clause.original_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const truncateText = (text: string, maxLength: number = 150) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  };

  return (
    <Card className={cn(
      "transition-all duration-200 hover:shadow-md",
      config.priority === 1 && "border-l-4 border-l-red-500",
      config.priority === 2 && "border-l-4 border-l-yellow-500",
      config.priority === 3 && "border-l-4 border-l-green-500"
    )}>
      <AccordionItem value={clause.clause_id} className="border-none">
        <AccordionTrigger 
          className="text-left hover:no-underline p-4 md:p-6 pb-4"
          onClick={() => setIsExpanded(!isExpanded)}
          aria-label={`${isExpanded ? 'Collapse' : 'Expand'} clause ${clause.clause_id} - ${config.label}`}
        >
          <div className="flex flex-1 items-start gap-4 w-full">
            <div className="flex items-center gap-3 flex-1 min-w-0">
              <Icon className={`mt-1 h-5 w-5 shrink-0 ${config.className.split(' ')[1]}`} aria-hidden="true" />
              <div className="flex-1 min-w-0">
                <div className="flex flex-wrap items-center gap-2 mb-2">
                  <Badge variant="outline" className={cn("text-xs font-medium", config.badgeClassName)}>
                    {config.label}
                  </Badge>
                  <Badge variant="secondary" className="text-xs">
                    <FileText className="h-3 w-3 mr-1" aria-hidden="true" />
                    {clause.clause_id}
                  </Badge>
                </div>
                <p className="font-semibold text-sm leading-relaxed">
                  {isExpanded ? clause.summary : truncateText(clause.summary)}
                </p>
                {clause.word_count && (
                  <p className="text-xs text-muted-foreground mt-1">
                    {clause.word_count} words
                  </p>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <div
                onClick={(e) => {
                  e.stopPropagation();
                  handleCopy();
                }}
                className="h-8 w-8 p-0 inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:bg-accent hover:text-accent-foreground cursor-pointer"
                aria-label={`Copy original text of clause ${clause.clause_id}`}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    e.stopPropagation();
                    handleCopy();
                  }
                }}
              >
                <Copy className="h-4 w-4" />
              </div>
              {isExpanded ? (
                <ChevronDown className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
              ) : (
                <ChevronRight className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
              )}
            </div>
          </div>
        </AccordionTrigger>
        <AccordionContent className="px-6 pb-6">
          <CardContent className="p-0">
            <div className="space-y-4">
              <div className="rounded-lg border bg-muted/30 p-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold text-sm text-foreground">Original Clause Text</h4>
                  <div className="flex items-center gap-2">
                    {copied && (
                      <span className="text-xs text-green-600 dark:text-green-400">
                        Copied!
                      </span>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleCopy}
                      className="h-8 px-2 text-xs"
                    >
                      <Copy className="h-3 w-3 mr-1" />
                      Copy
                    </Button>
                  </div>
                </div>
                <blockquote className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
                  {clause.original_text}
                </blockquote>
              </div>

              {clause.entities && clause.entities.length > 0 && (
                <div className="rounded-lg border bg-muted/30 p-4">
                  <h4 className="font-semibold text-sm text-foreground mb-3">Key Entities</h4>
                  <div className="flex flex-wrap gap-2">
                    {clause.entities.map((entity, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {entity}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex items-center justify-between text-xs text-muted-foreground pt-2 border-t">
                <span>Clause ID: {clause.clause_id}</span>
                {clause.word_count && (
                  <span>Word count: {clause.word_count}</span>
                )}
              </div>
            </div>
          </CardContent>
        </AccordionContent>
      </AccordionItem>
    </Card>
  );
}
