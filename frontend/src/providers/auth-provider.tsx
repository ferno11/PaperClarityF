"use client";

import React, { createContext, useEffect, useState } from "react";
import { onAuthStateChanged, User } from "firebase/auth";
import { auth } from "@/lib/firebase/config";
import { useRouter, usePathname } from "next/navigation";

interface AuthContextType {
  user: User | null;
  loading: boolean;
}

export const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
});

const PROTECTED_ROUTES = ["/dashboard"];
const PUBLIC_ROUTES = ["/login"];

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  useEffect(() => {
    // if (!loading) {
    //   const isProtectedRoute = PROTECTED_ROUTES.some(route => pathname.startsWith(route));
    //   const isPublicRoute = PUBLIC_ROUTES.some(route => pathname.startsWith(route));
    //   if (!user && isProtectedRoute) {
    //     router.push("/login");
    //   }
    //   if (user && isPublicRoute) {
    //     router.push("/dashboard");
    //   }
    // }
  }, [user, loading, pathname, router]);

  return (
    <AuthContext.Provider value={{ user, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
