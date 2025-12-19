const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export interface LoginRequest {
  username: string; // Backend expects 'username' but it's actually email
  password: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  name: string;
  email: string;
  role: string;
}

// Token storage key
const TOKEN_KEY = "auth_token";

// Get stored token
export const getToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY);
};

// Store token
export const setToken = (token: string): void => {
  localStorage.setItem(TOKEN_KEY, token);
};

// Remove token
export const removeToken = (): void => {
  localStorage.removeItem(TOKEN_KEY);
};

// API client with token handling
const apiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  const token = getToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Unauthorized - token might be invalid
      removeToken();
      throw new Error("Unauthorized");
    }
    const error = await response.json().catch(() => ({ detail: "An error occurred" }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
};

// Auth API calls
export const authApi = {
  login: async (email: string, password: string): Promise<TokenResponse> => {
    // Backend uses OAuth2PasswordRequestForm which expects 'username' instead of 'email'
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Invalid credentials" }));
      throw new Error(error.detail || "Invalid credentials");
    }

    const data = await response.json();
    setToken(data.access_token);
    return data;
  },

  register: async (name: string, email: string, password: string): Promise<User> => {
    return apiRequest<User>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ name, email, password }),
    });
  },

  getMe: async (): Promise<User> => {
    return apiRequest<User>("/auth/me");
  },

  logout: (): void => {
    removeToken();
  },
};

// Upload API calls
export interface FileListResponse {
  id: number;
  filename: string;
  file_size: number;
  upload_time: string;
  processed: boolean;
}

export const uploadApi = {
  getFiles: async (): Promise<FileListResponse[]> => {
    return apiRequest<FileListResponse[]>("/api/upload/files/");
  },

  uploadCsv: async (file: File, forecastDays: number = 30): Promise<any> => {
    const formData = new FormData();
    formData.append("file", file);
    
    const token = getToken();
    const response = await fetch(`${API_BASE_URL}/api/upload/csv/?forecast_days=${forecastDays}`, {
      method: "POST",
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Upload failed" }));
      throw new Error(error.detail || "Upload failed");
    }

    return response.json();
  },
};

// Generic API request helper (for other API calls)
export const api = {
  request: apiRequest,
};

// Dashboard API interfaces
export interface DashboardMetrics {
  total_revenue: { value: number; growth?: number };
  total_orders: { value: number; growth?: number };
  active_users: { value: number; growth?: number };
  avg_order_value: { value: number; growth?: number };
}

export interface CategoryPerformance {
  name: string;
  revenue: number;
  growth: number;
  rank: number;
}

export interface MonthlySales {
  month: string;
  month_number: number;
  year: number;
  revenue: number;
}

export interface ForecastPeriod {
  period: string;
  value: number;
  change: number;
  confidence: number;
  forecast_days: number;
}

export interface DashboardForecasts {
  periods: ForecastPeriod[];
}

export interface BiweeklySalesBucket {
  start: string; // ISO date
  end: string;   // ISO date
  label: string; // short label like MM/DD
  revenue: number;
}

// Dashboard API calls
export const dashboardApi = {
  getMetrics: async (): Promise<DashboardMetrics> => {
    return apiRequest<DashboardMetrics>("/api/upload/dashboard/metrics/");
  },

  getCategories: async (): Promise<CategoryPerformance[]> => {
    return apiRequest<CategoryPerformance[]>("/api/upload/dashboard/categories/");
  },

  getMonthlySales: async (): Promise<MonthlySales[]> => {
    return apiRequest<MonthlySales[]>("/api/upload/dashboard/monthly-sales/");
  },

  getForecasts: async (): Promise<DashboardForecasts> => {
    return apiRequest<DashboardForecasts>("/api/upload/dashboard/forecasts/");
  },

  getBiweeklySales: async (): Promise<BiweeklySalesBucket[]> => {
    return apiRequest<BiweeklySalesBucket[]>("/api/upload/dashboard/biweekly-sales/");
  },

  getBiweeklyForecasts: async (): Promise<BiweeklySalesBucket[]> => {
    return apiRequest<BiweeklySalesBucket[]>("/api/upload/dashboard/biweekly-forecasts/");
  },
};

