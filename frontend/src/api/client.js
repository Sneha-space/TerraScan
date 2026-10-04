import axios from "axios";
import config from "../config";

// Central API client - every request goes through here
const api = axios.create({
  baseURL: config.apiBaseUrl,
  timeout: config.timeout,
});

/**
 * One readable sentence for a failed request, for showing on screen.
 */
export function errorMessage(error, fallback = "Something went wrong.") {
  if (!error) return fallback;
  if (!error.response) {
    return `Couldn't reach the server at ${config.apiBaseUrl}. Check that the backend is running, then try again.`;
  }
  const detail = error.response.data?.detail;
  if (typeof detail === "string") return detail;
  return fallback;
}

export default api;
