"use client";

import React, { createContext, useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";

interface User {
  id: string;
  username: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: async () => false,
  logout: () => {},
});

const PROTECTED_ROUTES = ["/dashboard"];
const PUBLIC_ROUTES = ["/login"];

// Hardcoded credentials
const VALID_CREDENTIALS = {
  username: "root12345",
  password: "root12345"
};

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Temporarily disable localStorage check to force login page
    // Check if user is logged in from localStorage
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        // Comment out to force login page
        // setUser(JSON.parse(savedUser));
        setUser(null);
        localStorage.removeItem('user');
      } catch (error) {
        // If there's an error parsing, clear the invalid data
        localStorage.removeItem('user');
        setUser(null);
      }
    } else {
      setUser(null);
    }
    setLoading(false);
  }, []);

  const login = async (username: string, password: string): Promise<boolean> => {
    if (username === VALID_CREDENTIALS.username && password === VALID_CREDENTIALS.password) {
      const userData: User = {
        id: "1",
        username: username,
        email: `${username}@example.com`
      };
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      return true;
    }
    return false;
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
    router.push('/login');
  };

  useEffect(() => {
    if (!loading) {
      const isProtectedRoute = PROTECTED_ROUTES.some(route => pathname.startsWith(route));
      const isPublicRoute = PUBLIC_ROUTES.some(route => pathname.startsWith(route));
      if (!user && isProtectedRoute) {
        router.push("/login");
      }
      if (user && isPublicRoute) {
        router.push("/dashboard");
      }
    }
  }, [user, loading, pathname, router]);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
