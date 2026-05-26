import { api } from "./api";

export const chatbotService = {
  products: () => api.get("/api/chatbot/products").then((res) => res.data),
  index: (scanId) => api.post(`/api/chatbot/index/${scanId}`).then((res) => res.data),
  ask: (payload) => api.post("/api/chatbot/ask", payload).then((res) => res.data)
};
