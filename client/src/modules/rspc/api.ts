import axios from "axios";

const client = axios.create({
  baseURL: "/api/rspc",
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("auth_token") || sessionStorage.getItem("auth_token");
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

export const rspcApi = {
  getProposals: () => client.get("/proposals/").then((r) => r.data),
  createProposal: (data: any) => client.post("/proposals/", data).then((r) => r.data),
  approveProposal: (id: number, action: string, reason?: string) =>
    client.post(`/proposals/${id}/approve/`, { action, reason }).then((r) => r.data),

  getConsultancies: () => client.get("/consultancies/").then((r) => r.data),
  createConsultancy: (data: any) => client.post("/consultancies/", data).then((r) => r.data),

  getFinancialRequests: () => client.get("/financial-requests/").then((r) => r.data),
  createFinancialRequest: (data: any) => client.post("/financial-requests/", data).then((r) => r.data),

  getReports: () => client.get("/reports/").then((r) => r.data),
  createReport: (data: any) => client.post("/reports/", data).then((r) => r.data),
};
