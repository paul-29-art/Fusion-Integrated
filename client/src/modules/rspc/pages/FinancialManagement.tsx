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
  Alert,
} from "@mantine/core";
import { rspcApi } from "../api/api";

interface Props {
  userRole: string;
}

export default function FinancialManagement({ userRole }: Props) {
  const [finRequests, setFinRequests] = useState<any[]>([]);
  const [proposals, setProposals] = useState<any[]>([]);
  const [createModal, setCreateModal] = useState(false);

  const [formData, setFormData] = useState({
    proposal: 1,
    request_type: "DISBURSEMENT",
    budget_head: "Consumables & Lab Expenses",
    amount: 150000,
    justification: "",
  });

  const loadData = async () => {
    try {
      const [reqs, props] = await Promise.all([
        rspcApi.getFinancialRequests(),
        rspcApi.getProposals(),
      ]);
      setFinRequests(reqs);
      setProposals(props);
      if (props.length > 0) {
        setFormData((prev) => ({ ...prev, proposal: props[0].id }));
      }
    } catch {
      // Graceful fallback
    }
  };

  useEffect(() => {
    loadData();
  }, [userRole]);

  const handleCreate = async () => {
    try {
      await rspcApi.createFinancialRequest(formData);
      setCreateModal(false);
      setFormData({
        proposal: proposals[0]?.id || 1,
        request_type: "DISBURSEMENT",
        budget_head: "Consumables & Lab Expenses",
        amount: 150000,
        justification: "",
      });
      loadData();
    } catch {
      alert("Failed to submit financial request.");
    }
  };

  const handleAdminVerify = async (id: number, action: string) => {
    await rspcApi.adminVerifyFinance(id, action);
    loadData();
  };

  const handleDeanDecide = async (id: number, action: string) => {
    await rspcApi.deanDecideFinance(id, action);
    loadData();
  };

  const handleDirectorDecide = async (id: number, action: string) => {
    await rspcApi.directorDecideFinance(id, action);
    loadData();
  };

  const proposalSelectData = proposals.map((p) => ({
    value: String(p.id),
    label: `#${p.id} - ${p.title} (Bal: ₹${Number(p.remaining_balance || p.budget).toLocaleString("en-IN")})`,
  }));

  return (
    <Stack>
      <Card withBorder p="md">
        <Group justify="space-between" mb="md">
          <div>
            <Title order={4}>Financial & Fund Management (CW-RSPC-04)</Title>
            <Text size="sm" c="dimmed">
              Delegated Financial Powers: Dean Approval (&le; ₹5,00,000) | Director Escalation (&gt; ₹5,00,000) (BR-RSPC-032, BR-RSPC-033)
            </Text>
          </div>
          <Button onClick={() => setCreateModal(true)}>+ New Financial Request</Button>
        </Group>

        <Table striped highlightOnHover verticalSpacing="sm">
          <Table.Thead>
            <Table.Tr>
              <Table.Th>ID</Table.Th>
              <Table.Th>Project / Faculty</Table.Th>
              <Table.Th>Type & Head</Table.Th>
              <Table.Th>Amount (INR)</Table.Th>
              <Table.Th>Approval Route</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {finRequests.map((f) => (
              <Table.Tr key={f.id}>
                <Table.Td>#{f.id}</Table.Td>
                <Table.Td>
                  <Text fw={500}>{f.proposal_title || `Project #${f.proposal}`}</Text>
                  <Text size="xs" c="dimmed">Requester: {f.faculty_username || "Faculty"}</Text>
                </Table.Td>
                <Table.Td>
                  <Text size="sm">{f.request_type}</Text>
                  <Text size="xs" c="dimmed">{f.budget_head}</Text>
                </Table.Td>
                <Table.Td>
                  <Text fw={600}>₹{Number(f.amount).toLocaleString("en-IN")}</Text>
                </Table.Td>
                <Table.Td>
                  {f.requires_director_approval ? (
                    <Badge color="red" variant="light">&gt; ₹5L (Director Action)</Badge>
                  ) : (
                    <Badge color="blue" variant="light">Dean Delegated (&le; ₹5L)</Badge>
                  )}
                </Table.Td>
                <Table.Td>
                  <Badge color={f.status.includes("APPROVED") ? "green" : f.status === "REJECTED" ? "red" : "blue"}>
                    {f.status}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  <Group gap="xs">
                    {f.status === "SUBMITTED" && userRole === "RSPC_ADMIN" && (
                      <Button size="xs" color="teal" onClick={() => handleAdminVerify(f.id, "verify")}>Verify</Button>
                    )}
                    {f.status === "VERIFIED" && userRole === "DEAN_RSPC" && (
                      <Button size="xs" color="blue" onClick={() => handleDeanDecide(f.id, "approve")}>
                        {f.requires_director_approval ? "Forward to Director" : "Dean Sanction"}
                      </Button>
                    )}
                    {f.status === "FORWARDED_TO_DIRECTOR" && userRole === "DIRECTOR" && (
                      <Button size="xs" color="teal" onClick={() => handleDirectorDecide(f.id, "approve")}>Director Sanction</Button>
                    )}
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
            {finRequests.length === 0 && (
              <Table.Tr>
                <Table.Td colSpan={7}>
                  <Text ta="center" c="dimmed">No financial requests found.</Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Card>

      {/* Create Modal */}
      <Modal opened={createModal} onClose={() => setCreateModal(false)} title="New Fund / Expenditure Requisition">
        <Stack>
          <Select
            label="Associated Project"
            required
            value={String(formData.proposal)}
            onChange={(v) => setFormData({ ...formData, proposal: Number(v) || 1 })}
            data={proposalSelectData.length > 0 ? proposalSelectData : [{ value: "1", label: "Default Project #1" }]}
          />
          <Select
            label="Request Type"
            required
            value={formData.request_type}
            onChange={(v) => setFormData({ ...formData, request_type: v || "DISBURSEMENT" })}
            data={[
              { value: "DISBURSEMENT", label: "Fund Disbursement Request" },
              { value: "EXPENDITURE", label: "Direct Expenditure Claim" },
              { value: "TRAVEL", label: "Travel & Field Work Allowance" },
              { value: "CONTINGENCY", label: "Contingency Requisition" },
            ]}
          />
          <TextInput
            label="Budget Head"
            value={formData.budget_head}
            onChange={(e) => setFormData({ ...formData, budget_head: e.target.value })}
          />
          <NumberInput
            label="Amount (INR)"
            required
            value={formData.amount}
            onChange={(val) => setFormData({ ...formData, amount: Number(val) || 0 })}
          />

          {formData.amount > 500000 && (
            <Alert color="red" title="Director Approval Required (BR-RSPC-033)">
              Requisitions exceeding ₹5,00,000 exceed the Dean's delegated threshold and are automatically escalated to the Director.
            </Alert>
          )}

          <Textarea
            label="Justification & Purpose"
            required
            minRows={2}
            value={formData.justification}
            onChange={(e) => setFormData({ ...formData, justification: e.target.value })}
          />
          <Button fullWidth onClick={handleCreate}>Submit Financial Request</Button>
        </Stack>
      </Modal>
    </Stack>
  );
}
