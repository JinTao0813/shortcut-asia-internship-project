export interface Outlet {
  id?: number;
  name: string;
  category: string;
  address: string;
  maps_url: string;
  stock: number;
}

export interface Product {
  id?: number;
  name: string;
  link: string;
  category: string;
  price: string;
  image_url: string;
}

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

export interface ChatResponse {
  response?: string;
  message?: string;
}

export interface AuthResponse {
  success: boolean;
  message?: string;
}
