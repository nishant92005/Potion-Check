import { api } from "./api";

export const analysisService = {
  analyze: (payload) => api.post("/api/analysis/analyze", payload).then((res) => res.data),
  get: (id) => api.get(`/api/analysis/${id}`).then((res) => res.data),
  product: (barcode) => api.get(`/api/analysis/product/${barcode}`).then((res) => res.data),
  history: (params) => api.get("/api/history/", { params }).then((res) => res.data)
};
