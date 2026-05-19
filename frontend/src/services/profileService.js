import { api } from "./api";

export const profileService = {
  get: () => api.get("/api/profile/").then((res) => res.data),
  save: (payload) => api.post("/api/profile/", payload).then((res) => res.data)
};
