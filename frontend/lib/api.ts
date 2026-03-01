import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle 401 errors — refresh önce dene
let isRefreshing = false;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      // Refresh endpoint kendisi 401 dönerse döngüye girme
      if (originalRequest.url?.includes('/auth/refresh')) {
        localStorage.removeItem('access_token');
        window.location.href = '/tr/login';
        return Promise.reject(error);
      }

      originalRequest._retry = true;

      if (!isRefreshing) {
        isRefreshing = true;
        try {
          const token = localStorage.getItem('access_token');
          if (token) {
            const res = await api.post('/auth/refresh');
            const newToken = res.data.access_token;
            localStorage.setItem('access_token', newToken);
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            isRefreshing = false;
            return api(originalRequest);
          }
        } catch {
          // Refresh başarısız — login'e yönlendir
        }
        isRefreshing = false;
      }

      localStorage.removeItem('access_token');
      window.location.href = '/tr/login';
    }
    return Promise.reject(error);
  }
);

/**
 * apiSilent — 401 geldiğinde login'e yönlendirmez.
 * Chatbot geçmişi ve stats gibi auth-optional istekler için kullanın.
 */
export const apiSilent = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
});

apiSilent.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;
