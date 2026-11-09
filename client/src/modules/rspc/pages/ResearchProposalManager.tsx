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
  TextInput,
  NumberInput,
  Textarea,
  Select,
  Timeline,
} from "@mantine/core";
import { rspcApi } from "../api/api";

interface Props {
  userRole: string;
}

export default function ResearchProposalManager({ userRole }: Props) {
  const [proposals, setProposals] = useState<any[]>([]);
  const [createModal, setCreateModal] = useState(false);
  const [reviewModal, setReviewModal] = useState(false);
  const [historyModal, setHistoryModal] = useState(false);
  const [selectedProposal, setSelectedProposal] = useState<any>(null);
  const [decisions, setDecisions] = useState<any[]>([]);

  // Form state
  const [formData, setFormData] = useState({
    title: "",
    sponsor_agency: "",
    department: "CSE",
    co_pi: "",
    budget: 1500000,
    duration_months: 24,
    objectives: "",
    timeline_details: "Q1-Q2: Requirement Analysis & Design\nQ3-Q4: Implementation & Deployment",
    resource_requirements: "High-Performance Workstation, Cloud Compute GPU Credits",
  });

  // Review state
  const [reviewAction, setReviewAction] = useState<string>("approve");
  const [reviewRemarks, setReviewRemarks] = useState<string>("");

  const loadProposals = async () => {
    try {
      const data = await rspcApi.getProposals();
      setProposals(data);
    } catch {
      // Graceful fallback for demo
    }
  };

  useEffect(() => {
    loadProposals();
  }, [userRole]);

  const handleCreate = async () => {
    try {
      await rspcApi.createProposal(formData);
      setCreateModal(false);
      setFormData({
        title: "",
        sponsor_agency: "",
        department: "CSE",
        co_pi: "",
        budget: 1500000,
        duration_months: 24,
        objectives: "",
        timeline_details: "",
        resource_requirements: "",
      });
      loadProposals();
    } catch (err) {
      alert("Failed to create proposal. Ensure all mandatory fields are filled.");
    }
  };

  const handleSubmit = async (id: number) => {
    try {
      await rspcApi.submitProposal(id);
      loadProposals();
    } catch {
      alert("Could not submit proposal.");
    }
  };

  const openReviewModal = (proposal: any) => {
    setSelectedProposal(proposal);
    setReviewRemarks("");
    // Default action based on role
    if (userRole === "HOD") setReviewAction("recommend");
    else if (userRole === "RSPC_ADMIN") setReviewAction("verify");
    else if (userRole === "DEAN_RSPC") setReviewAction("approve");
    else if (userRole === "DIRECTOR") setReviewAction("approve");
    setReviewModal(true);
  };

  const handleReviewSubmit = async () => {
    if (!selectedProposal) return;
    try {
      if (userRole === "HOD") {
        await rspcApi.hodReviewProposal(selectedProposal.id, reviewAction, reviewRemarks);
      } else if (userRole === "RSPC_ADMIN") {
        await rspcApi.adminVerifyProposal(selectedProposal.id, reviewAction, reviewRemarks);
      } else if (userRole === "DEAN_RSPC") {
        await rspcApi.deanDecideProposal(selectedProposal.id, reviewAction, reviewRemarks);
      } else if (userRole === "DIRECTOR") {
        await rspcApi.directorDecideProposal(selectedProposal.id, reviewAction, reviewRemarks);
      }
      setReviewModal(false);
      loadProposals();
    } catch {
      alert("Failed to submit review decision.");
    }
  };

  const openHistoryModal = async (proposal: any) => {
    setSelectedProposal(proposal);
    try {
      const data = await rspcApi.getProposalDecisions(proposal.id);
      setDecisions(data);
    } catch {
      setDecisions([]);
    }
    setHistoryModal(true);
  };

  const getStatusColor = (status: string) => {
    if (status.includes("APPROVED")) return "green";
    if (status.includes("REJECTED")) return "red";
    if (status.includes("FORWARDED")) return "violet";
    if (status.includes("RECOMMENDED")) return "teal";
    if (status.includes("VERIFIED")) return "cyan";
    if (status === "SUBMITTED") return "blue";
    return "gray";
  };

  return (
    <Stack>
      <Card withBorder p="md">
        <Group justify="space-between" mb="md">
          <div>
            <Title order={4}>Sponsored Research Proposals (CW-RSPC-01)</Title>
            <Text size="sm" c="dimmed">
              Lifecycle: Faculty Submission &rarr; HoD Recommendation &rarr; Admin Verification &rarr; Dean Approval &rarr; Director Sanction
            </Text>
          </div>
          <Button onClick={() => setCreateModal(true)}>+ Submit Proposal</Button>
        </Group>

        <Table striped highlightOnHover verticalSpacing="sm">
          <Table.Thead>
            <Table.Tr>
              <Table.Th>ID</Table.Th>
              <Table.Th>Title</Table.Th>
              <Table.Th>PI / Dept</Table.Th>
              <Table.Th>Sponsor Agency</Table.Th>
              <Table.Th>Budget (INR)</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {proposals.map((p) => (
              <Table.Tr key={p.id}>
                <Table.Td>#{p.id}</Table.Td>
                <Table.Td>
                  <Text fw={500}>{p.title}</Text>
                  <Text size="xs" c="dimmed">{p.duration_months} Months</Text>
                </Table.Td>
                <Table.Td>
                  <Text size="sm">{p.pi_username || "Current User"}</Text>
                  <Text size="xs" c="dimmed">{p.department}</Text>
                </Table.Td>
                <Table.Td>{p.sponsor_agency}</Table.Td>
                <Table.Td>
                  <Text fw={600}>₹{Number(p.budget).toLocaleString("en-IN")}</Text>
                  {p.is_sanctioned && (
                    <Text size="xs" c="green">Sanctioned</Text>
                  )}
                </Table.Td>
                <Table.Td>
                  <Badge color={getStatusColor(p.status)} variant="filled">
                    {p.status}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  <Group gap="xs">
                    {p.status === "DRAFT" && (
                      <Button size="xs" color="teal" onClick={() => handleSubmit(p.id)}>
                        Submit
                      </Button>
                    )}
                    {userRole !== "FACULTY" && (
                      <Button size="xs" variant="light" onClick={() => openReviewModal(p)}>
                        Review
                      </Button>
                    )}
                    <Button size="xs" variant="subtle" color="gray" onClick={() => openHistoryModal(p)}>
                      History
                    </Button>
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
            {proposals.length === 0 && (
              <Table.Tr>
                <Table.Td colSpan={7}>
                  <Text ta="center" c="dimmed">No proposals found.</Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Card>

      {/* Proposal Create Modal */}
      <Modal opened={createModal} onClose={() => setCreateModal(false)} title="Submit Research Proposal" size="lg">
        <Stack>
          <TextInput
            label="Project Title"
            required
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="e.g. Edge Computing for Smart Grid Fault Detection"
          />
          <Group grow>
            <TextInput
              label="Funding / Sponsor Agency"
              required
              value={formData.sponsor_agency}
              onChange={(e) => setFormData({ ...formData, sponsor_agency: e.target.value })}
              placeholder="e.g. SERB / DST / ISRO"
            />
            <TextInput
              label="Department"
              value={formData.department}
              onChange={(e) => setFormData({ ...formData, department: e.target.value })}
            />
          </Group>
          <Group grow>
            <NumberInput
              label="Total Budget (INR)"
              required
              value={formData.budget}
              onChange={(val) => setFormData({ ...formData, budget: Number(val) || 0 })}
            />
            <NumberInput
              label="Duration (Months)"
              required
              value={formData.duration_months}
              onChange={(val) => setFormData({ ...formData, duration_months: Number(val) || 12 })}
            />
          </Group>
          <TextInput
            label="Co-Principal Investigator(s)"
            value={formData.co_pi}
            onChange={(e) => setFormData({ ...formData, co_pi: e.target.value })}
            placeholder="Optional Co-PI names"
          />
          <Textarea
            label="Project Objectives"
            required
            minRows={3}
            value={formData.objectives}
            onChange={(e) => setFormData({ ...formData, objectives: e.target.value })}
            placeholder="Key research questions and objectives"
          />
          <Textarea
            label="Timeline Details"
            minRows={2}
            value={formData.timeline_details}
            onChange={(e) => setFormData({ ...formData, timeline_details: e.target.value })}
          />
          <Textarea
            label="Resource Requirements"
            minRows={2}
            value={formData.resource_requirements}
            onChange={(e) => setFormData({ ...formData, resource_requirements: e.target.value })}
          />
          <Button fullWidth onClick={handleCreate}>Save & Create Proposal</Button>
        </Stack>
      </Modal>

      {/* Review Modal */}
      <Modal opened={reviewModal} onClose={() => setReviewModal(false)} title={`Review Proposal #${selectedProposal?.id} (${userRole})`}>
        <Stack>
          <Text size="sm"><b>Title:</b> {selectedProposal?.title}</Text>
          <Text size="sm"><b>Budget:</b> ₹{Number(selectedProposal?.budget).toLocaleString("en-IN")}</Text>
          <Text size="sm"><b>Current Status:</b> {selectedProposal?.status}</Text>

          {userRole === "HOD" && (
            <Select
              label="HoD Action"
              value={reviewAction}
              onChange={(v) => setReviewAction(v || "recommend")}
              data={[
                { value: "recommend", label: "Recommend to RSPC" },
                { value: "reject", label: "Do Not Recommend" },
              ]}
            />
          )}

          {userRole === "RSPC_ADMIN" && (
            <Select
              label="Admin Verification"
              value={reviewAction}
              onChange={(v) => setReviewAction(v || "verify")}
              data={[
                { value: "verify", label: "Verify Completeness & Forward" },
                { value: "reject", label: "Reject (Ineligible / Incomplete)" },
              ]}
            />
          )}

          {userRole === "DEAN_RSPC" && (
            <Select
              label="Dean RSPC Action"
              value={reviewAction}
              onChange={(v) => setReviewAction(v || "approve")}
              data={[
                { value: "approve", label: "Approve Proposal (Sanction)" },
                { value: "forward_director", label: "Forward to Director (High-Value / Strategic)" },
                { value: "reject", label: "Reject Proposal" },
              ]}
            />
          )}

          {userRole === "DIRECTOR" && (
            <Select
              label="Director Action"
              value={reviewAction}
              onChange={(v) => setReviewAction(v || "approve")}
              data={[
                { value: "approve", label: "Authorize & Approve" },
                { value: "reject", label: "Reject" },
              ]}
            />
          )}

          <Textarea
            label="Review Remarks"
            required
            value={reviewRemarks}
            onChange={(e) => setReviewRemarks(e.target.value)}
            placeholder="Official evaluation remarks and observations"
          />

          <Button fullWidth onClick={handleReviewSubmit}>Submit Decision</Button>
        </Stack>
      </Modal>

      {/* History Modal */}
      <Modal opened={historyModal} onClose={() => setHistoryModal(false)} title={`Decision History for Proposal #${selectedProposal?.id}`}>
        <Stack>
          <Timeline active={decisions.length - 1} bulletSize={24} lineWidth={2}>
            {decisions.map((d, index) => (
              <Timeline.Item key={index} title={`${d.reviewer_role} Decision: ${d.decision}`}>
                <Text size="xs" c="dimmed">{new Date(d.timestamp).toLocaleString()}</Text>
                <Text size="sm" mt={4}><b>Reviewer:</b> {d.reviewer_username}</Text>
                {d.remarks && <Text size="sm" c="gray.7"><b>Remarks:</b> {d.remarks}</Text>}
              </Timeline.Item>
            ))}
          </Timeline>
          {decisions.length === 0 && (
            <Text c="dimmed" ta="center">No review decisions recorded yet.</Text>
          )}
        </Stack>
      </Modal>
    </Stack>
  );
}
