import axios from "axios";

const client = axios.create({
  baseURL: "/api/rspc",
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("auth_token") || sessionStorage.getItem("auth_token");
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  const activeRole = localStorage.getItem("rspc_active_role");
  if (activeRole) {
    config.headers["X-RSPC-Role"] = activeRole;
  }
  return config;
});

export const rspcApi = {
  // Profile & Role
  getProfile: () => client.get("/profiles/me/").then((r) => r.data),
  switchRole: (role: string) => client.post("/profiles/switch_role/", { role }).then((r) => r.data),

  // Research Proposals (CW-01)
  getProposals: () => client.get("/proposals/").then((r) => r.data),
  createProposal: (data: any) => client.post("/proposals/", data).then((r) => r.data),
  submitProposal: (id: number) => client.post(`/proposals/${id}/submit/`).then((r) => r.data),
  hodReviewProposal: (id: number, action: string, remarks: string) =>
    client.post(`/proposals/${id}/hod_review/`, { action, remarks }).then((r) => r.data),
  adminVerifyProposal: (id: number, action: string, remarks: string) =>
    client.post(`/proposals/${id}/admin_verify/`, { action, remarks }).then((r) => r.data),
  deanDecideProposal: (id: number, action: string, remarks: string) =>
    client.post(`/proposals/${id}/dean_decide/`, { action, remarks }).then((r) => r.data),
  directorDecideProposal: (id: number, action: string, remarks: string) =>
    client.post(`/proposals/${id}/director_decide/`, { action, remarks }).then((r) => r.data),
  getProposalDecisions: (id: number) => client.get(`/proposals/${id}/decisions/`).then((r) => r.data),

  // Consultancy Projects (CW-02)
  getConsultancies: () => client.get("/consultancies/").then((r) => r.data),
  createConsultancy: (data: any) => client.post("/consultancies/", data).then((r) => r.data),
  submitConsultancy: (id: number) => client.post(`/consultancies/${id}/submit/`).then((r) => r.data),
  hodReviewConsultancy: (id: number, action: string, remarks: string) =>
    client.post(`/consultancies/${id}/hod_review/`, { action, remarks }).then((r) => r.data),
  adminVerifyConsultancy: (id: number, action: string, remarks: string) =>
    client.post(`/consultancies/${id}/admin_verify/`, { action, remarks }).then((r) => r.data),
  deanDecideConsultancy: (id: number, action: string, remarks: string) =>
    client.post(`/consultancies/${id}/dean_decide/`, { action, remarks }).then((r) => r.data),
  directorDecideConsultancy: (id: number, action: string, remarks: string) =>
    client.post(`/consultancies/${id}/director_decide/`, { action, remarks }).then((r) => r.data),
  createMilestone: (data: any) => client.post("/milestones/", data).then((r) => r.data),
  deliverMilestone: (id: number) => client.post(`/milestones/${id}/deliver/`).then((r) => r.data),
  settleMilestone: (id: number) => client.post(`/milestones/${id}/settle/`).then((r) => r.data),

  // Staff Appointments (CW-03)
  getStaffRequests: () => client.get("/staff-appointments/").then((r) => r.data),
  createStaffRequest: (data: any) => client.post("/staff-appointments/", data).then((r) => r.data),
  adminVerifyStaff: (id: number, action: string) =>
    client.post(`/staff-appointments/${id}/admin_verify/`, { action }).then((r) => r.data),
  recordSelection: (id: number, candidateName: string, remarks: string) =>
    client.post(`/staff-appointments/${id}/record_selection/`, { selected_candidate_name: candidateName, selection_committee_remarks: remarks }).then((r) => r.data),
  deanDecideStaff: (id: number, action: string) =>
    client.post(`/staff-appointments/${id}/dean_decide/`, { action }).then((r) => r.data),
  directorDecideStaff: (id: number, action: string) =>
    client.post(`/staff-appointments/${id}/director_decide/`, { action }).then((r) => r.data),

  // Financial Requests (CW-04)
  getFinancialRequests: () => client.get("/financial-requests/").then((r) => r.data),
  createFinancialRequest: (data: any) => client.post("/financial-requests/", data).then((r) => r.data),
  adminVerifyFinance: (id: number, action: string) =>
    client.post(`/financial-requests/${id}/admin_verify/`, { action }).then((r) => r.data),
  deanDecideFinance: (id: number, action: string) =>
    client.post(`/financial-requests/${id}/dean_decide/`, { action }).then((r) => r.data),
  directorDecideFinance: (id: number, action: string) =>
    client.post(`/financial-requests/${id}/director_decide/`, { action }).then((r) => r.data),

  // Procurement Requests (CW-05)
  getProcurementRequests: () => client.get("/procurements/").then((r) => r.data),
  createProcurementRequest: (data: any) => client.post("/procurements/", data).then((r) => r.data),
  adminVerifyProcurement: (id: number, action: string) =>
    client.post(`/procurements/${id}/admin_verify/`, { action }).then((r) => r.data),
  deanDecideProcurement: (id: number, action: string) =>
    client.post(`/procurements/${id}/dean_decide/`, { action }).then((r) => r.data),
  directorDecideProcurement: (id: number, action: string) =>
    client.post(`/procurements/${id}/director_decide/`, { action }).then((r) => r.data),

  // Reports & Project Closure (CW-06)
  getReports: () => client.get("/reports/").then((r) => r.data),
  createReport: (data: any) => client.post("/reports/", data).then((r) => r.data),
  acceptReport: (id: number) => client.post(`/reports/${id}/accept/`).then((r) => r.data),

  getClosures: () => client.get("/closures/").then((r) => r.data),
  createClosure: (data: any) => client.post("/closures/", data).then((r) => r.data),
  adminVerifyClosure: (id: number, action: string) =>
    client.post(`/closures/${id}/admin_verify/`, { action }).then((r) => r.data),
  deanDecideClosure: (id: number, action: string, remarks: string) =>
    client.post(`/closures/${id}/dean_decide/`, { action, remarks }).then((r) => r.data),
  directorDecideClosure: (id: number, action: string, remarks: string) =>
    client.post(`/closures/${id}/director_decide/`, { action, remarks }).then((r) => r.data),

  // Audit Logs & Notifications
  getAuditLogs: () => client.get("/audit-logs/").then((r) => r.data),
  getNotifications: () => client.get("/notifications/").then((r) => r.data),
  markNotificationRead: (id: number) => client.post(`/notifications/${id}/mark_as_read/`).then((r) => r.data),
};
