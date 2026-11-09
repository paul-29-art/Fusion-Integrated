import { useState, useEffect } from "react";
import {
  Card,
  Table,
  Badge,
  Button,
  Group,
  Stack,
  Title,
  Text,
  Modal,
  NumberInput,
  Textarea,
  Select,
  Checkbox,
} from "@mantine/core";
import { rspcApi } from "../api/api";

interface Props {
  userRole: string;
}

export default function ReportsAndClosure({ userRole }: Props) {
  const [reports, setReports] = useState<any[]>([]);
  const [closures, setClosures] = useState<any[]>([]);
  const [proposals, setProposals] = useState<any[]>([]);

  const [reportModal, setReportModal] = useState(false);
  const [closureModal, setClosureModal] = useState(false);

  const [reportForm, setReportForm] = useState({
    proposal: 1,
    report_type: "ANNUAL",
    work_summary: "",
    utilization_amount: 500000,
    milestone_achievements: "",
  });

  const [closureForm, setClosureForm] = useState({
    proposal: 1,
    closure_report_summary: "",
    unspent_balance: 0,
    asset_declaration_verified: true,
  });

  const loadData = async () => {
    try {
      const [reps, clos, props] = await Promise.all([
        rspcApi.getReports(),
        rspcApi.getClosures(),
        rspcApi.getProposals(),
      ]);
      setReports(reps);
      setClosures(clos);
      setProposals(props);
      if (props.length > 0) {
        setReportForm((prev) => ({ ...prev, proposal: props[0].id }));
        setClosureForm((prev) => ({ ...prev, proposal: props[0].id }));
      }
    } catch {
      // Graceful fallback
    }
  };

  useEffect(() => {
    loadData();
  }, [userRole]);

  const handleCreateReport = async () => {
    try {
      await rspcApi.createReport(reportForm);
      setReportModal(false);
      loadData();
    } catch {
      alert("Failed to submit progress report.");
    }
  };

  const handleAcceptReport = async (id: number) => {
    await rspcApi.acceptReport(id);
    loadData();
  };

  const handleCreateClosure = async () => {
    try {
      await rspcApi.createClosure(closureForm);
      setClosureModal(false);
      loadData();
    } catch {
      alert("Failed to submit closure report.");
    }
  };

  const handleAdminVerifyClosure = async (id: number, action: string) => {
    await rspcApi.adminVerifyClosure(id, action);
    loadData();
  };

  const handleDeanDecideClosure = async (id: number, action: string) => {
    await rspcApi.deanDecideClosure(id, action, "Dean Closure Review Completed");
    loadData();
  };

  const handleDirectorDecideClosure = async (id: number, action: string) => {
    await rspcApi.directorDecideClosure(id, action, "Director Archival Sanction Granted");
    loadData();
  };

  const proposalSelectData = proposals.map((p) => ({
    value: String(p.id),
    label: `#${p.id} - ${p.title}`,
  }));

  return (
    <Stack>
      {/* Progress & Utilization Reports */}
      <Card withBorder p="md">
        <Group justify="space-between" mb="md">
          <div>
            <Title order={4}>Periodic Progress & Utilization Reports (CFR-018, CFR-019)</Title>
            <Text size="sm" c="dimmed">
              Annual Progress Reports, Milestone Tracking & Utilization Certificates (UC-014)
            </Text>
          </div>
          <Button onClick={() => setReportModal(true)}>+ Submit Report</Button>
        </Group>

        <Table striped highlightOnHover verticalSpacing="sm">
          <Table.Thead>
            <Table.Tr>
              <Table.Th>ID</Table.Th>
              <Table.Th>Project</Table.Th>
              <Table.Th>Report Type</Table.Th>
              <Table.Th>Utilized Amount</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Action</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {reports.map((r) => (
              <Table.Tr key={r.id}>
                <Table.Td>#{r.id}</Table.Td>
                <Table.Td>
                  <Text fw={500}>{r.proposal_title || `Project #${r.proposal}`}</Text>
                  <Text size="xs" c="dimmed">By: {r.submitted_by_username || "Faculty"}</Text>
                </Table.Td>
                <Table.Td>{r.report_type}</Table.Td>
                <Table.Td>₹{Number(r.utilization_amount).toLocaleString("en-IN")}</Table.Td>
                <Table.Td>
                  <Badge color={r.status === "ACCEPTED" ? "green" : "blue"}>{r.status}</Badge>
                </Table.Td>
                <Table.Td>
                  {r.status === "SUBMITTED" && userRole !== "FACULTY" && (
                    <Button size="xs" color="teal" onClick={() => handleAcceptReport(r.id)}>Accept</Button>
                  )}
                </Table.Td>
              </Table.Tr>
            ))}
            {reports.length === 0 && (
              <Table.Tr>
                <Table.Td colSpan={6}><Text ta="center" c="dimmed">No reports submitted yet.</Text></Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Card>

      {/* Project Closure & Archival */}
      <Card withBorder p="md">
        <Group justify="space-between" mb="md">
          <div>
            <Title order={4}>Project Closure & Archival (CW-RSPC-06)</Title>
            <Text size="sm" c="dimmed">
              Verification of Financial Settlement Records, Asset Transfer & Dean/Director Archival (BR-RSPC-043)
            </Text>
          </div>
          <Button color="indigo" onClick={() => setClosureModal(true)}>+ Request Project Closure</Button>
        </Group>

        <Table striped highlightOnHover verticalSpacing="sm">
          <Table.Thead>
            <Table.Tr>
              <Table.Th>ID</Table.Th>
              <Table.Th>Project</Table.Th>
              <Table.Th>Settlement Status</Table.Th>
              <Table.Th>Asset Declaration</Table.Th>
              <Table.Th>Unspent Balance</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {closures.map((c) => (
              <Table.Tr key={c.id}>
                <Table.Td>#{c.id}</Table.Td>
                <Table.Td>
                  <Text fw={500}>{c.proposal_title || `Project #${c.proposal}`}</Text>
                  <Text size="xs" c="dimmed">PI: {c.faculty_username || "Faculty"}</Text>
                </Table.Td>
                <Table.Td>
                  <Badge color={c.financial_settlement_status === "CLEARED" ? "green" : "cyan"}>
                    {c.financial_settlement_status}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  {c.asset_declaration_verified ? (
                    <Badge color="green" variant="light">&check; Assets Verified</Badge>
                  ) : (
                    <Badge color="orange" variant="light">Pending Declaration</Badge>
                  )}
                </Table.Td>
                <Table.Td>₹{Number(c.unspent_balance).toLocaleString("en-IN")}</Table.Td>
                <Table.Td>
                  <Badge color={c.status === "ARCHIVED" ? "green" : c.status === "REJECTED" ? "red" : "blue"}>
                    {c.status}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  <Group gap="xs">
                    {c.status === "SUBMITTED" && userRole === "RSPC_ADMIN" && (
                      <Button size="xs" color="teal" onClick={() => handleAdminVerifyClosure(c.id, "verify")}>Verify</Button>
                    )}
                    {c.status === "VERIFIED" && userRole === "DEAN_RSPC" && (
                      <Button size="xs" color="blue" onClick={() => handleDeanDecideClosure(c.id, "approve")}>Dean Archive</Button>
                    )}
                    {c.status === "FORWARDED_TO_DIRECTOR" && userRole === "DIRECTOR" && (
                      <Button size="xs" color="teal" onClick={() => handleDirectorDecideClosure(c.id, "approve")}>Director Archive</Button>
                    )}
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
            {closures.length === 0 && (
              <Table.Tr>
                <Table.Td colSpan={7}><Text ta="center" c="dimmed">No closure records initiated.</Text></Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Card>

      {/* Progress Report Modal */}
      <Modal opened={reportModal} onClose={() => setReportModal(false)} title="Submit Progress / Utilization Report">
        <Stack>
          <Select
            label="Project"
            required
            value={String(reportForm.proposal)}
            onChange={(v) => setReportForm({ ...reportForm, proposal: Number(v) || 1 })}
            data={proposalSelectData.length > 0 ? proposalSelectData : [{ value: "1", label: "Default Project #1" }]}
          />
          <Select
            label="Report Category"
            required
            value={reportForm.report_type}
            onChange={(v) => setReportForm({ ...reportForm, report_type: v || "ANNUAL" })}
            data={[
              { value: "ANNUAL", label: "Annual Progress Report" },
              { value: "UTILIZATION", label: "Utilization Certificate (UC)" },
              { value: "FINAL_COMPLETION", label: "Final Project Completion Report" },
            ]}
          />
          <NumberInput
            label="Expenditure / Utilization Amount (INR)"
            value={reportForm.utilization_amount}
            onChange={(val) => setReportForm({ ...reportForm, utilization_amount: Number(val) || 0 })}
          />
          <Textarea
            label="Work Summary & Research Highlights"
            required
            minRows={3}
            value={reportForm.work_summary}
            onChange={(e) => setReportForm({ ...reportForm, work_summary: e.target.value })}
          />
          <Textarea
            label="Milestone Achievements & Publications"
            minRows={2}
            value={reportForm.milestone_achievements}
            onChange={(e) => setReportForm({ ...reportForm, milestone_achievements: e.target.value })}
          />
          <Button fullWidth onClick={handleCreateReport}>Submit Periodic Report</Button>
        </Stack>
      </Modal>

      {/* Project Closure Modal */}
      <Modal opened={closureModal} onClose={() => setClosureModal(false)} title="Initiate Project Closure (CW-RSPC-06)">
        <Stack>
          <Select
            label="Project to Close"
            required
            value={String(closureForm.proposal)}
            onChange={(v) => setClosureForm({ ...closureForm, proposal: Number(v) || 1 })}
            data={proposalSelectData.length > 0 ? proposalSelectData : [{ value: "1", label: "Default Project #1" }]}
          />
          <Textarea
            label="Executive Closure Summary & Deliverables Handover"
            required
            minRows={3}
            value={closureForm.closure_report_summary}
            onChange={(e) => setClosureForm({ ...closureForm, closure_report_summary: e.target.value })}
          />
          <NumberInput
            label="Unspent Grant Balance to be Refunded / Transferred (INR)"
            value={closureForm.unspent_balance}
            onChange={(val) => setClosureForm({ ...closureForm, unspent_balance: Number(val) || 0 })}
          />
          <Checkbox
            label="I certify that all project equipment and physical assets have been transferred to the Department inventory declaration."
            checked={closureForm.asset_declaration_verified}
            onChange={(e) => setClosureForm({ ...closureForm, asset_declaration_verified: e.currentTarget.checked })}
          />
          <Button fullWidth color="indigo" onClick={handleCreateClosure}>Submit for Closure & Archival</Button>
        </Stack>
      </Modal>
    </Stack>
  );
}
