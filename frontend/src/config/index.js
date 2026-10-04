// Settings that change between machines. The backend address comes from
// .env (VITE_API_BASE_URL) so nobody has to edit code to point elsewhere.

const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",

  // request timeout in milliseconds
  timeout: 30000,

  // must match MAX_UPLOAD_BYTES in backend/src/core/config.py
  maxFileSizeMB: 25,
  acceptedFileTypes: ["application/pdf", "image/jpeg", "image/png"],

  appName: "TerraScan",
  appTagline: "Land record verification",
};

export default config;
