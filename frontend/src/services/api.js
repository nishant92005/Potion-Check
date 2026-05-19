import axios from "axios";
import { useUserStore } from "../stores/useStores";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  withCredentials: true
});

api.interceptors.request.use((config) => {
  const token = useUserStore.getState().accessToken;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    const token = useUserStore.getState().accessToken;
    const isRefreshRequest = original?.url?.includes("/api/auth/refresh");
    if (error.response?.status === 401 && token && !isRefreshRequest && !original?._retry) {
      original._retry = true;
      try {
        const { data } = await api.post("/api/auth/refresh");
        useUserStore.getState().setAccessToken(data.access_token);
        original.headers.Authorization = `Bearer ${data.access_token}`;
        return api(original);
      } catch {
        useUserStore.getState().logout();
        window.location.href = "/profile";
      }
    }
    return Promise.reject(error);
  }
);
