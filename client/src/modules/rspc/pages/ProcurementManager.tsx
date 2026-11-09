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

export default function ProcurementManager({ userRole }: Props) {
  const [procurements, setProcurements] = useState<any[]>([]);
  const [proposals, setProposals] = useState<any[]>([]);
  const [createModal, setCreateModal] = useState(false);

  const [formData, setFormData] = useState({
    proposal: 1,
    item_type: "EQUIPMENT",
    item_name: "",
    estimated_cost: 250000,
    specifications: "",
  });

  const loadData = async () => {
    try {
      const [procs, props] = await Promise.all([
        rspcApi.getProcurementRequests(),
        rspcApi.getProposals(),
      ]);
      setProcurements(procs);
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
      await rspcApi.createProcurementRequest(formData);
      setCreateModal(false);
      setFormData({
        proposal: proposals[0]?.id || 1,
        item_type: "EQUIPMENT",
        item_name: "",
        estimated_cost: 250000,
        specifications: "",
      });
      loadData();
    } catch {
      alert("Failed to create procurement requisition.");
    }
  };

  const handleAdminVerify = async (id: number, action: string) => {
    await rspcApi.adminVerifyProcurement(id, action);
    loadData();
  };

  const handleDeanDecide = async (id: number, action: string) => {
    await rspcApi.deanDecideProcurement(id, action);
    loadData();
  };

  const handleDirectorDecide = async (id: number, action: string) => {
    await rspcApi.directorDecideProcurement(id, action);
    loadData();
  };

  const proposalSelectData = proposals.map((p) => ({
    value: String(p.id),
    label: `#${p.id} - ${p.title} (Sanctioned: ₹${Number(p.sanctioned_budget || p.budget).toLocaleString("en-IN")})`,
  }));

  return (
    <Stack>
      <Card withBorder p="md">
        <Group justify="space-between" mb="md">
          <div>
            <Title order={4}>Procurement Requisitions (CW-RSPC-05)</Title>
            <Text size="sm" c="dimmed">
              Equipment & Consumables: Sanctioned Budget Balance Validation & Approval Hierarchy (BR-RSPC-035, BR-RSPC-036)
            </Text>
          </div>
          <Button onClick={() => setCreateModal(true)}>+ Requisition Item</Button>
        </Group>

        <Table striped highlightOnHover verticalSpacing="sm">
          <Table.Thead>
            <Table.Tr>
              <Table.Th>ID</Table.Th>
              <Table.Th>Project / Requester</Table.Th>
              <Table.Th>Type & Item Name</Table.Th>
              <Table.Th>Estimated Cost</Table.Th>
              <Table.Th>Budget Checked</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {procurements.map((pr) => (
              <Table.Tr key={pr.id}>
                <Table.Td>#{pr.id}</Table.Td>
                <Table.Td>
                  <Text fw={500}>{pr.proposal_title || `Project #${pr.proposal}`}</Text>
                  <Text size="xs" c="dimmed">PI: {pr.faculty_username || "Faculty"}</Text>
                </Table.Td>
                <Table.Td>
                  <Text size="sm">{pr.item_name}</Text>
                  <Text size="xs" c="dimmed">{pr.item_type}</Text>
                </Table.Td>
                <Table.Td>
                  <Text fw={600}>₹{Number(pr.estimated_cost).toLocaleString("en-IN")}</Text>
                </Table.Td>
                <Table.Td>
                  {pr.sanctioned_budget_balance_checked ? (
                    <Badge color="green" variant="light">&check; Verified in Budget</Badge>
                  ) : (
                    <Badge color="orange" variant="light">Unchecked</Badge>
                  )}
                </Table.Td>
                <Table.Td>
                  <Badge color={pr.status.includes("APPROVED") ? "green" : pr.status === "REJECTED" ? "red" : "blue"}>
                    {pr.status}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  <Group gap="xs">
                    {pr.status === "SUBMITTED" && userRole === "RSPC_ADMIN" && (
                      <Button size="xs" color="teal" onClick={() => handleAdminVerify(pr.id, "verify")}>Verify</Button>
                    )}
                    {pr.status === "VERIFIED" && userRole === "DEAN_RSPC" && (
                      <Button size="xs" color="blue" onClick={() => handleDeanDecide(pr.id, "approve")}>Dean Sanction</Button>
                    )}
                    {pr.status === "FORWARDED_TO_DIRECTOR" && userRole === "DIRECTOR" && (
                      <Button size="xs" color="teal" onClick={() => handleDirectorDecide(pr.id, "approve")}>Director Sanction</Button>
                    )}
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
            {procurements.length === 0 && (
              <Table.Tr>
                <Table.Td colSpan={7}>
                  <Text ta="center" c="dimmed">No procurement requisitions found.</Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Card>

      {/* Create Modal */}
      <Modal opened={createModal} onClose={() => setCreateModal(false)} title="New Procurement Requisition" size="md">
        <Stack>
          <Select
            label="Associated Research Project"
            required
            value={String(formData.proposal)}
            onChange={(v) => setFormData({ ...formData, proposal: Number(v) || 1 })}
            data={proposalSelectData.length > 0 ? proposalSelectData : [{ value: "1", label: "Default Project #1" }]}
          />
          <Select
            label="Procurement Type"
            required
            value={formData.item_type}
            onChange={(v) => setFormData({ ...formData, item_type: v || "EQUIPMENT" })}
            data={[
              { value: "EQUIPMENT", label: "Capital Equipment" },
              { value: "CONSUMABLES", label: "Consumables & Lab Supplies" },
            ]}
          />
          <TextInput
            label="Item Name / Equipment Model"
            required
            value={formData.item_name}
            onChange={(e) => setFormData({ ...formData, item_name: e.target.value })}
            placeholder="e.g. Spectrum Analyzer / GPU Server"
          />
          <NumberInput
            label="Estimated Total Cost (INR)"
            required
            value={formData.estimated_cost}
            onChange={(val) => setFormData({ ...formData, estimated_cost: Number(val) || 0 })}
          />
          <Textarea
            label="Technical Specifications & Purpose"
            required
            minRows={2}
            value={formData.specifications}
            onChange={(e) => setFormData({ ...formData, specifications: e.target.value })}
          />
          <Alert color="teal" title="Budget Verification Note (BR-RSPC-035)">
            The requisition will automatically be verified against the project's sanctioned budget balance.
          </Alert>
          <Button fullWidth onClick={handleCreate}>Submit Requisition</Button>
        </Stack>
      </Modal>
    </Stack>
  );
}
