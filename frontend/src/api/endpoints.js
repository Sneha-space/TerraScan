// One function per backend route. Shapes are documented in
// docs/frontend-api-guide.md.

import api from "./client";

export const getHealth = () => api.get("/health");

export const getStats = () => api.get("/dashboard/stats");

/** @param {{status?: string, document_id?: number, limit?: number}} params */
export const listRecords = (params = {}) => api.get("/records", { params });

export const getRecord = (recordId) => api.get(`/records/${recordId}`);

/**
 * @param {Array<{field_id: number, corrected_value?: string, corrected_original?: string}>} corrections
 */
export const verifyRecord = (recordId, corrections = []) =>
  api.post(`/records/${recordId}/verify`, { corrections });

export const listDocuments = () => api.get("/documents");

export const uploadDocument = (file) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/documents/upload", form);
};

/** The uploaded file itself, as a Blob. */
export const getDocumentFile = (documentId) =>
  api.get(`/documents/${documentId}/file`, { responseType: "blob" });
