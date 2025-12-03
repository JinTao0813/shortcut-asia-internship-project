import axios, { AxiosError } from 'axios';
import { Outlet, Product, Food, Drink } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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

// ==================== Types ====================
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  history?: ChatMessage[];
}

export interface ChatResponse {
  response: string;
  session_id: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// ==================== Chat API ====================
// Endpoints: POST /chat/, POST /chat/query, GET /chat/history/{session_id}, DELETE /chat/history/{session_id}
export const chatAPI = {
  // Main chat endpoint with agent
  sendMessage: async (message: string, session_id: string = 'default', history: ChatMessage[] = []) => {
    const response = await api.post('/chat/', { message, session_id, history });
    return response.data;
  },

  // Direct RAG query (faster, no agent)
  queryRAG: async (query: string, top_k: number = 5) => {
    const response = await api.post('/chat/query', { query, top_k });
    return response.data;
  },

  // Get chat history
  getHistory: async (session_id: string) => {
    const response = await api.get(`/chat/history/${session_id}`);
    return response.data;
  },

  // Clear chat history
  clearHistory: async (session_id: string) => {
    const response = await api.delete(`/chat/history/${session_id}`);
    return response.data;
  },
};

// ==================== Auth API ====================
// Note: You'll need to implement these endpoints in your backend
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

// ==================== Outlets API ====================
// Endpoints: GET /outlets/, GET /outlets/{id}, POST /outlets/, PUT /outlets/{id}, DELETE /outlets/{id}, GET /outlets/search
export const outletsAPI = {
  // Get all outlets with pagination
  getAll: async (page: number = 1, per_page: number = 100) => {
    const response = await api.get(`/outlets/?page=${page}&per_page=${per_page}`);
    return response.data;
  },

  // Get single outlet by ID
  getById: async (id: number) => {
    const response = await api.get(`/outlets/${id}`);
    return response.data;
  },

  // Create new outlet
  create: async (outlet: Omit<Outlet, 'id'>) => {
    const response = await api.post('/outlets/', outlet);
    return response.data;
  },

  // Update outlet
  update: async (id: number, outlet: Partial<Omit<Outlet, 'id'>>) => {
    const response = await api.put(`/outlets/${id}`, outlet);
    return response.data;
  },

  // Delete outlet
  delete: async (id: number) => {
    const response = await api.delete(`/outlets/${id}`);
    return response.data;
  },

  // Search outlets
  search: async (params: {
    name?: string;
    category?: string;
    address?: string;
  }) => {
    const queryParams = new URLSearchParams();
    if (params.name) queryParams.append('name', params.name);
    if (params.category) queryParams.append('category', params.category);
    if (params.address) queryParams.append('address', params.address);
    
    const response = await api.get(`/outlets/search?${queryParams.toString()}`);
    return response.data;
  },
};

// ==================== Products API ====================
// Endpoints: GET /products/, GET /products/{id}, POST /products/, PUT /products/{id}, DELETE /products/{id}, GET /products/search
export const productsAPI = {
  // Get all products with pagination
  getAll: async (page: number = 1, per_page: number = 100) => {
    const response = await api.get(`/products/?page=${page}&per_page=${per_page}`);
    return response.data;
  },

  // Get single product by ID
  getById: async (id: number) => {
    const response = await api.get(`/products/${id}`);
    return response.data;
  },

  // Create new product
  create: async (product: Omit<Product, 'id'>) => {
    const response = await api.post('/products/', product);
    return response.data;
  },

  // Update product
  update: async (id: number, product: Partial<Omit<Product, 'id'>>) => {
    const response = await api.put(`/products/${id}`, product);
    return response.data;
  },

  // Delete product
  delete: async (id: number) => {
    const response = await api.delete(`/products/${id}`);
    return response.data;
  },

  // Search products
  search: async (params: {
    name?: string;
    category?: string;
    min_price?: number;
    max_price?: number;
  }) => {
    const queryParams = new URLSearchParams();
    if (params.name) queryParams.append('name', params.name);
    if (params.category) queryParams.append('category', params.category);
    if (params.min_price !== undefined) queryParams.append('min_price', params.min_price.toString());
    if (params.max_price !== undefined) queryParams.append('max_price', params.max_price.toString());
    
    const response = await api.get(`/products/search?${queryParams.toString()}`);
    return response.data;
  },
};

// ==================== Food API ====================
export const foodAPI = {
  // Get all food items with pagination
  getAll: async (page: number = 1, per_page: number = 100) => {
    const response = await api.get(`/food/?page=${page}&per_page=${per_page}`);
    return response.data;
  },

  // Get single food item by ID
  getById: async (id: number) => {
    const response = await api.get(`/food/${id}`);
    return response.data;
  },

  // Create new food item
  create: async (food: Omit<Food, 'id'>) => {
    const response = await api.post('/food/', food);
    return response.data;
  },

  // Update food item
  update: async (id: number, food: Partial<Omit<Food, 'id'>>) => {
    const response = await api.put(`/food/${id}`, food);
    return response.data;
  },

  // Delete food item
  delete: async (id: number) => {
    const response = await api.delete(`/food/${id}`);
    return response.data;
  },

  // Search food items
  search: async (params: {
    name?: string;
    category?: string;
    min_price?: number;
    max_price?: number;
  }) => {
    const queryParams = new URLSearchParams();
    if (params.name) queryParams.append('name', params.name);
    if (params.category) queryParams.append('category', params.category);
    if (params.min_price !== undefined) queryParams.append('min_price', params.min_price.toString());
    if (params.max_price !== undefined) queryParams.append('max_price', params.max_price.toString());
    
    const response = await api.get(`/food/search?${queryParams.toString()}`);
    return response.data;
  },
};

// ==================== Drinks API ====================
export const drinksAPI = {
  // Get all drinks with pagination
  getAll: async (page: number = 1, per_page: number = 100) => {
    const response = await api.get(`/drinks/?page=${page}&per_page=${per_page}`);
    return response.data;
  },

  // Get single drink by ID
  getById: async (id: number) => {
    const response = await api.get(`/drinks/${id}`);
    return response.data;
  },

  // Create new drink
  create: async (drink: Omit<Drink, 'id'>) => {
    const response = await api.post('/drinks/', drink);
    return response.data;
  },

  // Update drink
  update: async (id: number, drink: Partial<Omit<Drink, 'id'>>) => {
    const response = await api.put(`/drinks/${id}`, drink);
    return response.data;
  },

  // Delete drink
  delete: async (id: number) => {
    const response = await api.delete(`/drinks/${id}`);
    return response.data;
  },

  // Search drinks
  search: async (params: {
    name?: string;
    category?: string;
    min_price?: number;
    max_price?: number;
  }) => {
    const queryParams = new URLSearchParams();
    if (params.name) queryParams.append('name', params.name);
    if (params.category) queryParams.append('category', params.category);
    if (params.min_price !== undefined) queryParams.append('min_price', params.min_price.toString());
    if (params.max_price !== undefined) queryParams.append('max_price', params.max_price.toString());
    
    const response = await api.get(`/drinks/search?${queryParams.toString()}`);
    return response.data;
  },
};

// ==================== Embeddings API ====================
// Endpoints: POST /embeddings/reindex, GET /embeddings/status
export const embeddingsAPI = {
  // Reindex embeddings after CRUD operations
  reindex: async () => {
    const response = await api.post('/embeddings/reindex');
    return response.data;
  },

  // Get index status
  getStatus: async () => {
    const response = await api.get('/embeddings/status');
    return response.data;
  },
};

// Export default API object
export default {
  chat: chatAPI,
  auth: authAPI,
  outlets: outletsAPI,
  products: productsAPI,
  food: foodAPI,
  drinks: drinksAPI,
  embeddings: embeddingsAPI,
};