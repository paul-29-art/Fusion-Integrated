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
} from "@mantine/core";
import { rspcApi } from "../api/api";

interface Props {
  userRole: string;
}

export default function StaffAppointmentManager({ userRole }: Props) {
  const [requests, setRequests] = useState<any[]>([]);
  const [createModal, setCreateModal] = useState(false);
  const [selectionModal, setSelectionModal] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<any>(null);

  const [formData, setFormData] = useState({
    position_title: "Junior Research Fellow (JRF)",
    duration_months: 12,
    stipend_amount: 37000,
    stipend_structure: "DST Norms + 18% HRA",
    advertisement_details: "National portal and institute circular notice",
  });

  const [candidateName, setCandidateName] = useState("");
  const [selectionRemarks, setSelectionRemarks] = useState("");

  const loadRequests = async () => {
    try {
      const data = await rspcApi.getStaffRequests();
      setRequests(data);
    } catch {
      // Graceful fallback
    }
  };

  useEffect(() => {
    loadRequests();
  }, [userRole]);

  const handleCreate = async () => {
    try {
      await rspcApi.createStaffRequest(formData);
      setCreateModal(false);
      loadRequests();
    } catch {
      alert("Failed to submit staff appointment request.");
    }
  };

  const handleAdminVerify = async (id: number, action: string) => {
    await rspcApi.adminVerifyStaff(id, action);
    loadRequests();
  };

  const openSelectionModal = (req: any) => {
    setSelectedRequest(req);
    setCandidateName("");
    setSelectionRemarks("");
    setSelectionModal(true);
  };

  const handleSaveSelection = async () => {
    if (!selectedRequest) return;
    try {
      await rspcApi.recordSelection(selectedRequest.id, candidateName, selectionRemarks);
      setSelectionModal(false);
      loadRequests();
    } catch {
      alert("Could not record selection.");
    }
  };

  const handleDeanDecide = async (id: number, action: string) => {
    await rspcApi.deanDecideStaff(id, action);
    loadRequests();
  };

  const handleDirectorDecide = async (id: number, action: string) => {
    await rspcApi.directorDecideStaff(id, action);
    loadRequests();
  };

  return (
    <Stack>
      <Card withBorder p="md">
        <Group justify="space-between" mb="md">
          <div>
            <Title order={4}>Project Staff Appointments (CW-RSPC-03)</Title>
            <Text size="sm" c="dimmed">
              Request, Admin Advertisement/Verification, Selection Committee Recommendation & Dean/Director Approvals
            </Text>
          </div>
          <Button onClick={() => setCreateModal(true)}>+ Request Appointment</Button>
        </Group>

        <Table striped highlightOnHover verticalSpacing="sm">
          <Table.Thead>
            <Table.Tr>
              <Table.Th>ID</Table.Th>
              <Table.Th>Position & Faculty</Table.Th>
              <Table.Th>Duration</Table.Th>
              <Table.Th>Stipend (Monthly)</Table.Th>
              <Table.Th>Selected Candidate</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {requests.map((r) => (
              <Table.Tr key={r.id}>
                <Table.Td>#{r.id}</Table.Td>
                <Table.Td>
                  <Text fw={500}>{r.position_title}</Text>
                  <Text size="xs" c="dimmed">PI: {r.faculty_username || "Current Faculty"}</Text>
                </Table.Td>
                <Table.Td>{r.duration_months} Months</Table.Td>
                <Table.Td>₹{Number(r.stipend_amount).toLocaleString("en-IN")}</Table.Td>
                <Table.Td>{r.selected_candidate_name || <Text size="xs" c="dimmed">Pending Selection</Text>}</Table.Td>
                <Table.Td>
                  <Badge color={r.status.includes("APPROVED") ? "green" : r.status === "REJECTED" ? "red" : "blue"}>
                    {r.status}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  <Group gap="xs">
                    {r.status === "REQUESTED" && userRole === "RSPC_ADMIN" && (
                      <Button size="xs" color="teal" onClick={() => handleAdminVerify(r.id, "verify")}>Verify</Button>
                    )}
                    {r.status === "ADMIN_VERIFIED" && (
                      <Button size="xs" variant="light" onClick={() => openSelectionModal(r)}>Record Selection</Button>
                    )}
                    {r.status === "RECOMMENDATION_RECORDED" && userRole === "DEAN_RSPC" && (
                      <Button size="xs" color="teal" onClick={() => handleDeanDecide(r.id, "approve")}>Dean Sanction</Button>
                    )}
                    {r.status === "FORWARDED_TO_DIRECTOR" && userRole === "DIRECTOR" && (
                      <Button size="xs" color="blue" onClick={() => handleDirectorDecide(r.id, "approve")}>Director Sanction</Button>
                    )}
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
            {requests.length === 0 && (
              <Table.Tr>
                <Table.Td colSpan={7}>
                  <Text ta="center" c="dimmed">No staff appointment requests recorded.</Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Card>

      {/* Create Modal */}
      <Modal opened={createModal} onClose={() => setCreateModal(false)} title="New Staff Appointment Request">
        <Stack>
          <Select
            label="Position Title"
            required
            value={formData.position_title}
            onChange={(v) => setFormData({ ...formData, position_title: v || "JRF" })}
            data={[
              { value: "Junior Research Fellow (JRF)", label: "Junior Research Fellow (JRF)" },
              { value: "Senior Research Fellow (SRF)", label: "Senior Research Fellow (SRF)" },
              { value: "Project Associate / Assistant", label: "Project Associate / Assistant" },
              { value: "Post-Doctoral Fellow (PDF)", label: "Post-Doctoral Fellow (PDF)" },
            ]}
          />
          <Group grow>
            <NumberInput
              label="Stipend Amount (INR/Month)"
              required
              value={formData.stipend_amount}
              onChange={(val) => setFormData({ ...formData, stipend_amount: Number(val) || 0 })}
            />
            <NumberInput
              label="Appointment Duration (Months)"
              required
              value={formData.duration_months}
              onChange={(val) => setFormData({ ...formData, duration_months: Number(val) || 12 })}
            />
          </Group>
          <TextInput
            label="Stipend Norms / Structure"
            value={formData.stipend_structure}
            onChange={(e) => setFormData({ ...formData, stipend_structure: e.target.value })}
          />
          <Textarea
            label="Advertisement Channels & Details"
            value={formData.advertisement_details}
            onChange={(e) => setFormData({ ...formData, advertisement_details: e.target.value })}
          />
          <Button fullWidth onClick={handleCreate}>Submit Staff Request</Button>
        </Stack>
      </Modal>

      {/* Selection Modal (UC-022) */}
      <Modal opened={selectionModal} onClose={() => setSelectionModal(false)} title="Record Selection Recommendation (UC-022)">
        <Stack>
          <TextInput
            label="Selected Candidate Full Name"
            required
            value={candidateName}
            onChange={(e) => setCandidateName(e.target.value)}
            placeholder="e.g. Ramesh Kumar Sharma"
          />
          <Textarea
            label="Selection Committee Evaluation & Remarks"
            required
            value={selectionRemarks}
            onChange={(e) => setSelectionRemarks(e.target.value)}
            placeholder="Committee interview score, qualification verification, and recommendation remarks"
          />
          <Button fullWidth onClick={handleSaveSelection}>Submit Selection Recommendation</Button>
        </Stack>
      </Modal>
    </Stack>
  );
}
