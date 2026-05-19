import { api } from "./api";

export const scannerService = {
  barcode: (barcode) => api.post("/api/scanner/barcode", { barcode }).then((res) => res.data),
  analyzeBarcode: (payload) => api.post("/api/scanner/barcode/analyze", payload).then((res) => res.data),
  upload: (file, onUploadProgress) => {
    const form = new FormData();
    form.append("file", file);
    return api.post("/api/scanner/upload", form, { onUploadProgress }).then((res) => res.data);
  },
  text: (ingredients_text) => api.post("/api/scanner/text", { ingredients_text }).then((res) => res.data)
};
