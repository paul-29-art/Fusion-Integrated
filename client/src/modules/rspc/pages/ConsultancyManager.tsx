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
  Alert,
  Select,
} from "@mantine/core";
import { rspcApi } from "../api/api";

interface Props {
  userRole: string;
}

export default function ConsultancyManager({ userRole }: Props) {
  const [consultancies, setConsultancies] = useState<any[]>([]);
  const [createModal, setCreateModal] = useState(false);
  const [milestoneModal, setMilestoneModal] = useState(false);
  const [reviewModal, setReviewModal] = useState(false);
  const [selectedConsultancy, setSelectedConsultancy] = useState<any>(null);

  const [formData, setFormData] = useState({
    title: "",
    client_name: "",
    client_type: "Private Industry",
    scope_of_work: "",
    deliverables: "",
    total_cost: 600000,
  });

  const [milestoneForm, setMilestoneForm] = useState({
    title: "",
    deliverable_description: "",
    amount: 200000,
  });

  const [reviewAction, setReviewAction] = useState<string>("approve");
  const [reviewRemarks, setReviewRemarks] = useState<string>("");

  const loadConsultancies = async () => {
    try {
      const data = await rspcApi.getConsultancies();
      setConsultancies(data);
    } catch {
      // Graceful fallback
    }
  };

  useEffect(() => {
    loadConsultancies();
  }, [userRole]);

  const handleCreate = async () => {
    try {
      await rspcApi.createConsultancy(formData);
      setCreateModal(false);
      setFormData({
        title: "",
        client_name: "",
        client_type: "Private Industry",
        scope_of_work: "",
        deliverables: "",
        total_cost: 600000,
      });
      loadConsultancies();
    } catch {
      alert("Failed to register consultancy project.");
    }
  };

  const handleSubmit = async (id: number) => {
    try {
      await rspcApi.submitConsultancy(id);
      loadConsultancies();
    } catch {
      alert("Could not submit consultancy project.");
    }
  };

  const openMilestoneModal = (c: any) => {
    setSelectedConsultancy(c);
    setMilestoneModal(true);
  };

  const handleAddMilestone = async () => {
    if (!selectedConsultancy) return;
    try {
      await rspcApi.createMilestone({
        consultancy: selectedConsultancy.id,
        title: milestoneForm.title,
        deliverable_description: milestoneForm.deliverable_description,
        amount: milestoneForm.amount,
      });
      setMilestoneModal(false);
      setMilestoneForm({ title: "", deliverable_description: "", amount: 200000 });
      loadConsultancies();
    } catch {
      alert("Could not add milestone.");
    }
  };

  const handleDeliverMilestone = async (id: number) => {
    await rspcApi.deliverMilestone(id);
    loadConsultancies();
  };

  const handleSettleMilestone = async (id: number) => {
    await rspcApi.settleMilestone(id);
    loadConsultancies();
  };

  const openReviewModal = (c: any) => {
    setSelectedConsultancy(c);
    setReviewRemarks("");
    if (userRole === "HOD") setReviewAction("recommend");
    else if (userRole === "RSPC_ADMIN") setReviewAction("verify");
    else if (userRole === "DEAN_RSPC") setReviewAction("approve");
    else if (userRole === "DIRECTOR") setReviewAction("approve");
    setReviewModal(true);
  };

  const handleReviewSubmit = async () => {
    if (!selectedConsultancy) return;
    try {
      if (userRole === "HOD") {
        await rspcApi.hodReviewConsultancy(selectedConsultancy.id, reviewAction, reviewRemarks);
      } else if (userRole === "RSPC_ADMIN") {
        await rspcApi.adminVerifyConsultancy(selectedConsultancy.id, reviewAction, reviewRemarks);
      } else if (userRole === "DEAN_RSPC") {
        await rspcApi.deanDecideConsultancy(selectedConsultancy.id, reviewAction, reviewRemarks);
      } else if (userRole === "DIRECTOR") {
        await rspcApi.directorDecideConsultancy(selectedConsultancy.id, reviewAction, reviewRemarks);
      }
      setReviewModal(false);
      loadConsultancies();
    } catch {
      alert("Failed to submit review decision.");
    }
  };

  const instShare = (formData.total_cost * 0.30).toLocaleString("en-IN");
  const piShare = (formData.total_cost * 0.70).toLocaleString("en-IN");

  return (
    <Stack>
      <Card withBorder p="md">
        <Group justify="space-between" mb="md">
          <div>
            <Title order={4}>Consultancy Projects (CW-RSPC-02)</Title>
            <Text size="sm" c="dimmed">
              Institutional Revenue Sharing: 30% Institutional Overhead & 70% Investigator Share (BR-RSPC-011)
            </Text>
          </div>
          <Button onClick={() => setCreateModal(true)}>+ Register Consultancy</Button>
        </Group>

        <Table striped highlightOnHover verticalSpacing="sm">
          <Table.Thead>
            <Table.Tr>
              <Table.Th>ID</Table.Th>
              <Table.Th>Title & Client</Table.Th>
              <Table.Th>Total Fee</Table.Th>
              <Table.Th>Institute Share (30%)</Table.Th>
              <Table.Th>PI Share (70%)</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {consultancies.map((c) => (
              <Table.Tr key={c.id}>
                <Table.Td>#{c.id}</Table.Td>
                <Table.Td>
                  <Text fw={500}>{c.title}</Text>
                  <Text size="xs" c="dimmed">Client: {c.client_name} ({c.client_type})</Text>
                </Table.Td>
                <Table.Td>
                  <Text fw={600}>₹{Number(c.total_cost).toLocaleString("en-IN")}</Text>
                </Table.Td>
                <Table.Td c="dimmed">₹{Number(c.institutional_share).toLocaleString("en-IN")}</Table.Td>
                <Table.Td c="green" fw={600}>₹{Number(c.investigator_share).toLocaleString("en-IN")}</Table.Td>
                <Table.Td>
                  <Badge color={c.status.includes("APPROVED") ? "green" : c.status === "ACTIVE" ? "teal" : "blue"}>
                    {c.status}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  <Group gap="xs">
                    {c.status === "DRAFT" && (
                      <Button size="xs" color="teal" onClick={() => handleSubmit(c.id)}>Submit</Button>
                    )}
                    {userRole !== "FACULTY" && (
                      <Button size="xs" variant="light" onClick={() => openReviewModal(c)}>Review</Button>
                    )}
                    <Button size="xs" variant="subtle" onClick={() => openMilestoneModal(c)}>+ Milestone</Button>
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
            {consultancies.length === 0 && (
              <Table.Tr>
                <Table.Td colSpan={7}>
                  <Text ta="center" c="dimmed">No consultancy projects registered yet.</Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Card>

      {/* Registration Modal */}
      <Modal opened={createModal} onClose={() => setCreateModal(false)} title="Register Consultancy Project" size="lg">
        <Stack>
          <TextInput
            label="Consultancy Title"
            required
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="e.g. Structural Reliability Assessment for Metro Viaducts"
          />
          <Group grow>
            <TextInput
              label="Client Name"
              required
              value={formData.client_name}
              onChange={(e) => setFormData({ ...formData, client_name: e.target.value })}
              placeholder="e.g. L&T Infrastructure / BHEL"
            />
            <TextInput
              label="Client Type"
              value={formData.client_type}
              onChange={(e) => setFormData({ ...formData, client_type: e.target.value })}
            />
          </Group>
          <NumberInput
            label="Total Consultancy Fee (INR)"
            required
            value={formData.total_cost}
            onChange={(val) => setFormData({ ...formData, total_cost: Number(val) || 0 })}
          />

          <Alert color="blue" title="Revenue Sharing Policy Breakdown (BR-RSPC-011)">
            Institute Overhead Share (30%): <b>₹{instShare}</b><br />
            Principal Investigator & Team Share (70%): <b>₹{piShare}</b>
          </Alert>

          <Textarea
            label="Scope of Work"
            required
            value={formData.scope_of_work}
            onChange={(e) => setFormData({ ...formData, scope_of_work: e.target.value })}
          />
          <Textarea
            label="Key Deliverables"
            required
            value={formData.deliverables}
            onChange={(e) => setFormData({ ...formData, deliverables: e.target.value })}
          />

          <Button fullWidth onClick={handleCreate}>Save & Register Project</Button>
        </Stack>
      </Modal>

      {/* Add Milestone Modal */}
      <Modal opened={milestoneModal} onClose={() => setMilestoneModal(false)} title={`Milestones for #${selectedConsultancy?.id}`}>
        <Stack>
          <TextInput
            label="Milestone Title"
            required
            value={milestoneForm.title}
            onChange={(e) => setMilestoneForm({ ...milestoneForm, title: e.target.value })}
            placeholder="e.g. Preliminary Simulation Report"
          />
          <NumberInput
            label="Milestone Billing Amount (INR)"
            required
            value={milestoneForm.amount}
            onChange={(val) => setMilestoneForm({ ...milestoneForm, amount: Number(val) || 0 })}
          />
          <Textarea
            label="Deliverable Description"
            value={milestoneForm.deliverable_description}
            onChange={(e) => setMilestoneForm({ ...milestoneForm, deliverable_description: e.target.value })}
          />
          <Button onClick={handleAddMilestone}>Add Milestone</Button>

          {selectedConsultancy?.milestones && selectedConsultancy.milestones.length > 0 && (
            <Table mt="sm">
              <Table.Thead>
                <Table.Tr><Table.Th>Title</Table.Th><Table.Th>Amount</Table.Th><Table.Th>Status</Table.Th><Table.Th>Action</Table.Th></Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {selectedConsultancy.milestones.map((m: any) => (
                  <Table.Tr key={m.id}>
                    <Table.Td>{m.title}</Table.Td>
                    <Table.Td>₹{Number(m.amount).toLocaleString("en-IN")}</Table.Td>
                    <Table.Td><Badge color={m.status === "SETTLED" ? "green" : "blue"}>{m.status}</Badge></Table.Td>
                    <Table.Td>
                      {m.status === "PENDING" && (
                        <Button size="xs" variant="light" onClick={() => handleDeliverMilestone(m.id)}>Mark Delivered</Button>
                      )}
                      {m.status === "SUBMITTED" && userRole !== "FACULTY" && (
                        <Button size="xs" color="teal" onClick={() => handleSettleMilestone(m.id)}>Settle Payment</Button>
                      )}
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          )}
        </Stack>
      </Modal>

      {/* Review Modal */}
      <Modal opened={reviewModal} onClose={() => setReviewModal(false)} title={`Review Consultancy #${selectedConsultancy?.id} (${userRole})`}>
        <Stack>
          <Text size="sm"><b>Title:</b> {selectedConsultancy?.title}</Text>
          <Text size="sm"><b>Total Cost:</b> ₹{Number(selectedConsultancy?.total_cost).toLocaleString("en-IN")}</Text>

          <Select
            label="Decision Action"
            value={reviewAction}
            onChange={(v) => setReviewAction(v || "approve")}
            data={[
              { value: "approve", label: "Approve / Recommend" },
              { value: "forward_director", label: "Forward to Director" },
              { value: "reject", label: "Reject" },
            ]}
          />
          <Textarea
            label="Remarks"
            value={reviewRemarks}
            onChange={(e) => setReviewRemarks(e.target.value)}
          />
          <Button fullWidth onClick={handleReviewSubmit}>Submit Review</Button>
        </Stack>
      </Modal>
    </Stack>
  );
}
