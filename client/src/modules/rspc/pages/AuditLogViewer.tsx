import { useState, useEffect } from "react";
import {
  Card,
  Table,
  Badge,
  Group,
  Title,
  Text,
  TextInput,
  Code,
} from "@mantine/core";
import { rspcApi } from "../api/api";

export default function AuditLogViewer() {
  const [logs, setLogs] = useState<any[]>([]);
  const [search, setSearch] = useState("");

  const loadLogs = async () => {
    try {
      const data = await rspcApi.getAuditLogs();
      setLogs(data);
    } catch {
      // Graceful fallback
    }
  };

  useEffect(() => {
    loadLogs();
  }, []);

  const filteredLogs = logs.filter(
    (l) =>
      l.action.toLowerCase().includes(search.toLowerCase()) ||
      l.entity_type.toLowerCase().includes(search.toLowerCase()) ||
      (l.username && l.username.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <Card withBorder p="md">
      <Group justify="space-between" mb="md">
        <div>
          <Title order={4}>Regulatory Audit & Compliance Logs (BR-RSPC-050, CFR-002)</Title>
          <Text size="sm" c="dimmed">
            Immutable audit record of all project submissions, reviews, financial escalations, and role switches
          </Text>
        </div>
        <TextInput
          placeholder="Filter by action, entity, user..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          w={300}
        />
      </Group>

      <Table striped highlightOnHover verticalSpacing="xs">
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Timestamp</Table.Th>
            <Table.Th>Action</Table.Th>
            <Table.Th>Entity</Table.Th>
            <Table.Th>User</Table.Th>
            <Table.Th>Details</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {filteredLogs.map((l) => (
            <Table.Tr key={l.id}>
              <Table.Td>
                <Text size="xs">{new Date(l.timestamp).toLocaleString()}</Text>
              </Table.Td>
              <Table.Td>
                <Badge color="blue" variant="light">{l.action}</Badge>
              </Table.Td>
              <Table.Td>
                <Text size="sm">{l.entity_type} #{l.entity_id}</Text>
              </Table.Td>
              <Table.Td>
                <Text size="sm" fw={500}>{l.username || "System"}</Text>
              </Table.Td>
              <Table.Td>
                <Code block>{JSON.stringify(l.details)}</Code>
              </Table.Td>
            </Table.Tr>
          ))}
          {filteredLogs.length === 0 && (
            <Table.Tr>
              <Table.Td colSpan={5}>
                <Text ta="center" c="dimmed">No audit logs matching search criteria.</Text>
              </Table.Td>
            </Table.Tr>
          )}
        </Table.Tbody>
      </Table>
    </Card>
  );
}
