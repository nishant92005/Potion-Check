import { api } from "./api";

export const authService = {
  register: (payload) => api.post("/api/auth/register", payload).then((res) => res.data),
  login: (payload) => api.post("/api/auth/login", payload).then((res) => res.data),
  logout: () => api.post("/api/auth/logout").then((res) => res.data),
  me: () => api.get("/api/auth/me").then((res) => res.data)
};
