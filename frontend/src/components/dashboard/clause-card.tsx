import type { Clause } from "@/lib/types";
import {
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { ShieldAlert, ShieldCheck, ShieldQuestion, ShieldX } from "lucide-react";

type ClauseCardProps = {
  clause: Clause;
};

const riskConfig = {
  High: {
    label: "High Risk",
    icon: ShieldAlert,
    className: "bg-red-500/10 text-red-700 border-red-500/20 hover:bg-red-500/20 dark:text-red-400",
  },
  Medium: {
    label: "Medium Risk",
    icon: ShieldQuestion,
    className: "bg-yellow-500/10 text-yellow-700 border-yellow-500/20 hover:bg-yellow-500/20 dark:text-yellow-400",
  },
  Low: {
    label: "Low Risk",
    icon: ShieldCheck,
    className: "bg-green-500/10 text-green-700 border-green-500/20 hover:bg-green-500/20 dark:text-green-400",
  },
  Unknown: {
    label: "Unknown",
    icon: ShieldX,
    className: "bg-gray-500/10 text-gray-700 border-gray-500/20 hover:bg-gray-500/20 dark:text-gray-400",
  }
};

export function ClauseCard({ clause }: ClauseCardProps) {
  const config = riskConfig[clause.risk_level] || riskConfig.Unknown;
  const Icon = config.icon;

  return (
    <AccordionItem value={clause.clause_id}>
      <AccordionTrigger className="text-left hover:no-underline">
        <div className="flex flex-1 items-start gap-4">
          <Icon className={`mt-1 h-5 w-5 shrink-0 ${config.className.split(' ')[1]}`} />
          <div className="flex-1">
            <p className="font-semibold">{clause.summary}</p>
            <p className="text-sm text-muted-foreground mt-1">{clause.clause_id}</p>
          </div>
          <Badge variant="outline" className={`ml-4 shrink-0 ${config.className}`}>
            {config.label}
          </Badge>
        </div>
      </AccordionTrigger>
      <AccordionContent className="pl-11">
        <div className="prose prose-sm max-w-none rounded-md border border-dashed bg-muted/50 p-4 text-muted-foreground">
          <p className="mb-2 font-semibold not-prose text-foreground">Original Clause Text</p>
          <blockquote className="not-prose">{clause.original_text}</blockquote>
          {clause.entities && clause.entities.length > 0 && (
            <>
              <p className="mt-4 mb-2 font-semibold not-prose text-foreground">Key Entities</p>
              <div className="not-prose flex flex-wrap gap-2">
                {clause.entities.map((entity, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {entity}
                  </Badge>
                ))}
              </div>
            </>
          )}
          {clause.word_count && (
            <p className="mt-4 text-xs text-muted-foreground not-prose">
              Word count: {clause.word_count}
            </p>
          )}
        </div>
      </AccordionContent>
    </AccordionItem>
  );
}
