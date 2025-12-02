'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '@/lib/api';

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const checkAuth = async () => {
    try {
      await authAPI.checkAuth();
      setIsAuthenticated(true);
    } catch {
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const login = async (password: string): Promise<boolean> => {
    try {
      await authAPI.login(password);
      setIsAuthenticated(true);
      return true;
    } catch {
      return false;
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, isLoading, login, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
