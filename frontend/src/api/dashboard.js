import api from "./client";

/**
 * Get dashboard data: status counts + needs_review, auto_approved and verified
 * lists. Each row carries owner_name, khasra_number, survey_number (null when
 * not found).
 */
export const getDashboard = () => {
  return api.get("/dashboard");
};
