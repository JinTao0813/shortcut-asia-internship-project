import axios, { AxiosError } from 'axios';
import { Outlet, Product } from '@/types';

// const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
const API_BASE_URL ='http://localhost:8001';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
  timeout: 10000,
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Don't log expected errors
    const url = error.config?.url || '';
    const status = error.response?.status;
    const isAuthCheck = url.includes('/admin/check');
    const isLogin = url.includes('/admin/login');
    const is401 = status === 401;
    
    // Skip logging for:
    // 1. Auth check returning 401 (not logged in)
    // 2. Login returning 401 (wrong password - will be handled by UI)
    if ((isAuthCheck && is401) || (isLogin && is401)) {
      return Promise.reject(error);
    }
    
    // Log unexpected errors
    console.error('API Error Details:', {
      message: error.message,
      code: error.code,
      status: status,
      statusText: error.response?.statusText,
      url: url,
      method: error.config?.method,
      data: error.response?.data,
    });
    return Promise.reject(error);
  }
);

// Chat API
export const chatAPI = {
  sendMessage: async (message: string, session_id: string = '1') => {
    const response = await api.post('/chat/', { message, session_id });
    return response.data;
  },
};

// Auth API
export const authAPI = {
  login: async (password: string) => {
    const response = await api.post('/admin/login', { password });
    return response.data;
  },
  logout: async () => {
    const response = await api.post('/admin/logout');
    return response.data;
  },
  checkAuth: async () => {
    const response = await api.get('/admin/check');
    return response.data;
  },
};

// Outlets API
export const outletsAPI = {
  getAll: async () => {
    const response = await api.get('/outlets/');
    return response.data;
  },
  create: async (outlet: Omit<Outlet, 'id'>) => {
    const response = await api.post('/outlets/create', outlet);
    return response.data;
  },
  update: async (id: number, outlet: Omit<Outlet, 'id'>) => {
    const response = await api.put(`/outlets/${id}`, outlet);
    return response.data;
  },
  delete: async (id: number) => {
    const response = await api.delete(`/outlets/${id}`);
    return response.data;
  },
};

// Products API
export const productsAPI = {
  getAll: async () => {
    const response = await api.get('/products/all');
    return response.data;
  },
  create: async (product: Omit<Product, 'id'>) => {
    const response = await api.post('/products/create', product);
    return response.data;
  },
  update: async (id: number, product: Omit<Product, 'id'>) => {
    const response = await api.put(`/products/${id}`, product);
    return response.data;
  },
  delete: async (id: number) => {
    const response = await api.delete(`/products/${id}`);
    return response.data;
  },
};
