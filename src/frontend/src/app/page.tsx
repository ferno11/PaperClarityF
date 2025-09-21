"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Always redirect to login page first
    router.push("/login");
  }, [router]);

  return (
    <div className="flex h-screen w-screen items-center justify-center bg-background p-8">
      <div className="w-full max-w-md space-y-4">
        <div className="text-center">
          <h2 className="text-2xl font-bold">Redirecting to login...</h2>
          <p className="text-muted-foreground">Please wait while we redirect you to the login page.</p>
        </div>
      </div>
    </div>
  );
}
