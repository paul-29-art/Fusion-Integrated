import { useState, useEffect } from "react";
import {
  Container, Title, Text, Tabs, Card, Table, Badge, Button,
  Modal, TextInput, NumberInput, Textarea, Group, Stack, Alert,
} from "@mantine/core";
import { rspcApi } from "../api";

export default function RSPCDashboard() {
  const [activeTab, setActiveTab] = useState<string | null>("proposals");
  const [proposals, setProposals] = useState<any[]>([]);
  const [consultancies, setConsultancies] = useState<any[]>([]);
  const [finRequests, setFinRequests] = useState<any[]>([]);
  const [reports, setReports] = useState<any[]>([]);

  const [modal, setModal] = useState<string | null>(null);
  const [form, setForm] = useState<any>({
    title: "", agency: "", budget: 500000, client: "", cost: 100000,
    projId: 1, amount: 50000, reqType: "DISBURSEMENT", text: ""
  });

  const loadData = async () => {
    try {
      const [p, c, f, r] = await Promise.all([
        rspcApi.getProposals(), rspcApi.getConsultancies(),
        rspcApi.getFinancialRequests(), rspcApi.getReports()
      ]);
      setProposals(p); setConsultancies(c); setFinRequests(f); setReports(r);
    } catch { /* fallback */ }
  };

  useEffect(() => { loadData(); }, []);

  const submitProposal = async () => {
    await rspcApi.createProposal({
      title: form.title, sponsor_agency: form.agency, budget: form.budget,
      abstract: form.text, duration_months: 12
    });
    setModal(null); loadData();
  };

  const submitConsultancy = async () => {
    await rspcApi.createConsultancy({
      title: form.title, client_name: form.client, total_cost: form.cost
    });
    setModal(null); loadData();
  };

  const submitFinance = async () => {
    await rspcApi.createFinancialRequest({
      proposal: form.projId, amount: form.amount, request_type: form.reqType, justification: form.text
    });
    setModal(null); loadData();
  };

  const submitReport = async () => {
    await rspcApi.createReport({ proposal: form.projId, summary: form.text, report_type: "ANNUAL" });
    setModal(null); loadData();
  };

  return (
    <Container size="xl" py="lg">
      <Group justify="space-between" mb="lg">
        <div>
          <Title order={2}>RSPC Management Portal</Title>
          <Text c="dimmed" size="sm">Research, Sponsored Projects & Consultancy (IIITDM Jabalpur)</Text>
        </div>
      </Group>

      <Tabs value={activeTab} onChange={setActiveTab}>
        <Tabs.List mb="md">
          <Tabs.Tab value="proposals">Research Proposals</Tabs.Tab>
          <Tabs.Tab value="consultancy">Consultancy Projects</Tabs.Tab>
          <Tabs.Tab value="finance">Financial Requests</Tabs.Tab>
          <Tabs.Tab value="reports">Project Reports</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="proposals">
          <Card withBorder p="md">
            <Group justify="space-between" mb="md">
              <Title order={4}>Sponsored Research Proposals</Title>
              <Button size="sm" onClick={() => setModal("proposal")}>+ New Proposal</Button>
            </Group>
            <Table striped highlightOnHover>
              <Table.Thead>
                <Table.Tr><Table.Th>Title</Table.Th><Table.Th>Agency</Table.Th><Table.Th>Budget</Table.Th><Table.Th>Status</Table.Th><Table.Th>Action</Table.Th></Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {proposals.map((p) => (
                  <Table.Tr key={p.id}>
                    <Table.Td>{p.title}</Table.Td><Table.Td>{p.sponsor_agency}</Table.Td>
                    <Table.Td>₹{Number(p.budget).toLocaleString("en-IN")}</Table.Td>
                    <Table.Td><Badge color={p.status.includes("APPROVED") ? "green" : "blue"}>{p.status}</Badge></Table.Td>
                    <Table.Td>
                      {p.status === "SUBMITTED" && <Button size="xs" variant="light" color="teal" onClick={async () => { await rspcApi.approveProposal(p.id, "hod_approve"); loadData(); }}>HoD Endorse</Button>}
                      {p.status === "HOD_APPROVED" && <Button size="xs" variant="light" color="blue" onClick={async () => { await rspcApi.approveProposal(p.id, "dean_approve"); loadData(); }}>Dean Sanction</Button>}
                    </Table.Td>
                  </Table.Tr>
                ))}
                {proposals.length === 0 && <Table.Tr><Table.Td colSpan={5}><Text c="dimmed" ta="center">No proposals found.</Text></Table.Td></Table.Tr>}
              </Table.Tbody>
            </Table>
          </Card>
        </Tabs.Panel>

        <Tabs.Panel value="consultancy">
          <Card withBorder p="md">
            <Group justify="space-between" mb="md">
              <Title order={4}>Consultancy Projects (30% Institute / 70% PI Share)</Title>
              <Button size="sm" onClick={() => setModal("consultancy")}>+ Register Consultancy</Button>
            </Group>
            <Table striped highlightOnHover>
              <Table.Thead>
                <Table.Tr><Table.Th>Title</Table.Th><Table.Th>Client</Table.Th><Table.Th>Fee</Table.Th><Table.Th>Inst. (30%)</Table.Th><Table.Th>Faculty (70%)</Table.Th><Table.Th>Status</Table.Th></Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {consultancies.map((c) => (
                  <Table.Tr key={c.id}>
                    <Table.Td>{c.title}</Table.Td><Table.Td>{c.client_name}</Table.Td>
                    <Table.Td>₹{Number(c.total_cost).toLocaleString("en-IN")}</Table.Td>
                    <Table.Td c="dimmed">₹{Number(c.institutional_share).toLocaleString("en-IN")}</Table.Td>
                    <Table.Td c="green" fw={500}>₹{Number(c.investigator_share).toLocaleString("en-IN")}</Table.Td>
                    <Table.Td><Badge color="cyan">{c.status}</Badge></Table.Td>
                  </Table.Tr>
                ))}
                {consultancies.length === 0 && <Table.Tr><Table.Td colSpan={6}><Text c="dimmed" ta="center">No projects found.</Text></Table.Td></Table.Tr>}
              </Table.Tbody>
            </Table>
          </Card>
        </Tabs.Panel>

        <Tabs.Panel value="finance">
          <Card withBorder p="md">
            <Group justify="space-between" mb="md">
              <Title order={4}>Fund Disbursements & Procurement Requisitions</Title>
              <Button size="sm" onClick={() => setModal("finance")}>+ New Request</Button>
            </Group>
            <Table striped highlightOnHover>
              <Table.Thead>
                <Table.Tr><Table.Th>Project</Table.Th><Table.Th>Type</Table.Th><Table.Th>Amount</Table.Th><Table.Th>Escalation</Table.Th><Table.Th>Status</Table.Th></Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {finRequests.map((f) => (
                  <Table.Tr key={f.id}>
                    <Table.Td>{f.proposal_title || `#${f.proposal}`}</Table.Td><Table.Td>{f.request_type}</Table.Td>
                    <Table.Td>₹{Number(f.amount).toLocaleString("en-IN")}</Table.Td>
                    <Table.Td>{f.requires_director_approval ? <Badge color="red">&gt; ₹5L (Director)</Badge> : <Badge color="gray">Standard</Badge>}</Table.Td>
                    <Table.Td><Badge color={f.status === "APPROVED" ? "green" : "orange"}>{f.status}</Badge></Table.Td>
                  </Table.Tr>
                ))}
                {finRequests.length === 0 && <Table.Tr><Table.Td colSpan={5}><Text c="dimmed" ta="center">No financial requests found.</Text></Table.Td></Table.Tr>}
              </Table.Tbody>
            </Table>
          </Card>
        </Tabs.Panel>

        <Tabs.Panel value="reports">
          <Card withBorder p="md">
            <Group justify="space-between" mb="md">
              <Title order={4}>Project Progress & Closure Reports</Title>
              <Button size="sm" onClick={() => setModal("report")}>+ Submit Report</Button>
            </Group>
            <Table striped highlightOnHover>
              <Table.Thead>
                <Table.Tr><Table.Th>Project</Table.Th><Table.Th>Type</Table.Th><Table.Th>Summary</Table.Th><Table.Th>Status</Table.Th></Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {reports.map((r) => (
                  <Table.Tr key={r.id}>
                    <Table.Td>{r.proposal_title || `#${r.proposal}`}</Table.Td><Table.Td>{r.report_type}</Table.Td>
                    <Table.Td>{r.summary}</Table.Td><Table.Td><Badge color="teal">{r.status}</Badge></Table.Td>
                  </Table.Tr>
                ))}
                {reports.length === 0 && <Table.Tr><Table.Td colSpan={4}><Text c="dimmed" ta="center">No reports found.</Text></Table.Td></Table.Tr>}
              </Table.Tbody>
            </Table>
          </Card>
        </Tabs.Panel>
      </Tabs>

      <Modal opened={modal === "proposal"} onClose={() => setModal(null)} title="Submit Research Proposal">
        <Stack>
          <TextInput label="Proposal Title" required value={form.title} onChange={(e) => setForm({ ...form, title: e.currentTarget.value })} />
          <TextInput label="Sponsor Agency" required value={form.agency} onChange={(e) => setForm({ ...form, agency: e.currentTarget.value })} />
          <NumberInput label="Total Budget (INR)" required value={form.budget} onChange={(v) => setForm({ ...form, budget: v })} />
          <Textarea label="Abstract" value={form.text} onChange={(e) => setForm({ ...form, text: e.currentTarget.value })} />
          <Button fullWidth onClick={submitProposal}>Submit to HoD</Button>
        </Stack>
      </Modal>

      <Modal opened={modal === "consultancy"} onClose={() => setModal(null)} title="Register Consultancy Project">
        <Stack>
          <TextInput label="Project Title" required value={form.title} onChange={(e) => setForm({ ...form, title: e.currentTarget.value })} />
          <TextInput label="Client Name" required value={form.client} onChange={(e) => setForm({ ...form, client: e.currentTarget.value })} />
          <NumberInput label="Total Fee (INR)" required value={form.cost} onChange={(v) => setForm({ ...form, cost: v })} />
          <Alert color="blue" title="Revenue Share Preview">
            Institute (30%): ₹{(Number(form.cost) * 0.30).toLocaleString("en-IN")} | PI (70%): ₹{(Number(form.cost) * 0.70).toLocaleString("en-IN")}
          </Alert>
          <Button fullWidth onClick={submitConsultancy}>Register</Button>
        </Stack>
      </Modal>

      <Modal opened={modal === "finance"} onClose={() => setModal(null)} title="New Financial Request">
        <Stack>
          <NumberInput label="Project ID" required value={form.projId} onChange={(v) => setForm({ ...form, projId: v })} />
          <NumberInput label="Amount (INR)" required value={form.amount} onChange={(v) => setForm({ ...form, amount: v })} />
          {Number(form.amount) > 500000 && <Alert color="red" title="Director Approval Required">Requests &gt; ₹5L require Director sanction.</Alert>}
          <Textarea label="Justification" required value={form.text} onChange={(e) => setForm({ ...form, text: e.currentTarget.value })} />
          <Button fullWidth onClick={submitFinance}>Submit</Button>
        </Stack>
      </Modal>

      <Modal opened={modal === "report"} onClose={() => setModal(null)} title="Submit Project Report">
        <Stack>
          <NumberInput label="Project ID" required value={form.projId} onChange={(v) => setForm({ ...form, projId: v })} />
          <Textarea label="Summary & Outcomes" required value={form.text} onChange={(e) => setForm({ ...form, text: e.currentTarget.value })} />
          <Button fullWidth onClick={submitReport}>Submit</Button>
        </Stack>
      </Modal>
    </Container>
  );
}
