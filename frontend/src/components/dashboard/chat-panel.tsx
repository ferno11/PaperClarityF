"use client";

import React, { useState, useRef, useEffect } from "react";
import { CornerDownLeft, FileUp, Mic, Paperclip } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter
} from "@/components/ui/card";
import type { ChatMessage } from "@/lib/types";
import { ScrollArea } from "../ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "../ui/avatar";
import { Logo } from "../icons";

type ChatPanelProps = {
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  onReset: () => void;
};

export function ChatPanel({ messages, onSendMessage, onReset }: ChatPanelProps) {
  const [input, setInput] = useState("");
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = () => {
    if (input.trim()) {
      onSendMessage(input);
      setInput("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <Card className="flex-grow flex flex-col h-[500px] md:h-auto">
      <CardHeader className="flex flex-row items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="p-2 bg-primary/10 rounded-full">
            <Logo className="w-6 h-6 text-primary" />
          </div>
          <div>
            <CardTitle>Ask Your Document</CardTitle>
            <CardDescription>
              Ask questions and get AI-powered answers.
            </CardDescription>
          </div>
        </div>
        <Button variant="ghost" size="sm" onClick={onReset} aria-label="Start new analysis">
            <FileUp className="h-4 w-4 mr-2" />
            <span className="hidden sm:inline">New Analysis</span>
        </Button>
      </CardHeader>
      <CardContent className="flex-1 overflow-hidden">
        <ScrollArea className="h-[300px] md:h-[400px] pr-4" ref={scrollAreaRef}>
          <div className="space-y-4">
            {messages.length === 0 ? (
                <div className="text-center text-muted-foreground p-8">
                    <p>No messages yet. Ask a question to get started, like "What are the confidentiality obligations?"</p>
                </div>
            ) : messages.map((message) => (
              <div
                key={message.id}
                className={`flex items-start gap-3 ${
                  message.role === "user" ? "justify-end" : ""
                }`}
                role="article"
                aria-label={`Message from ${message.role}`}
              >
                {message.role === "assistant" && (
                  <Avatar className="h-8 w-8" aria-hidden="true">
                    <AvatarFallback>
                      <Logo className="h-5 w-5" />
                    </AvatarFallback>
                  </Avatar>
                )}
                <div
                  className={`max-w-[85%] md:max-w-[75%] rounded-lg p-3 ${
                    message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  }`}
                >
                  <p className="text-sm">{message.content}</p>
                   {message.references && message.references.length > 0 && (
                      <div className="mt-2">
                        <p className="text-xs font-semibold mb-1">References:</p>
                        <div className="flex flex-wrap gap-1">
                          {message.references.map((ref, i) => (
                            <Badge key={i} variant="secondary" aria-label={`Reference to ${ref}`}>{ref}</Badge>
                          ))}
                        </div>
                      </div>
                    )}
                </div>
                 {message.role === "user" && (
                  <Avatar className="h-8 w-8" aria-hidden="true">
                    <AvatarFallback>U</AvatarFallback>
                  </Avatar>
                )}
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
      <CardFooter>
        <div className="relative w-full">
            <Textarea
              placeholder="Ask about your document..."
              className="resize-none border-border pr-16"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              aria-label="Type your question about the document"
              disabled={messages.some(msg => msg.content === "...")}
            />
            <Button 
              type="submit" 
              size="icon" 
              className="absolute right-2.5 top-1/2 -translate-y-1/2 h-8 w-8" 
              onClick={handleSend} 
              disabled={!input.trim() || messages.some(msg => msg.content === "...")}
              aria-label="Send message"
            >
              <CornerDownLeft className="h-4 w-4" />
              <span className="sr-only">Send</span>
            </Button>
        </div>
      </CardFooter>
    </Card>
  );
}
