import { useState, useEffect } from "react";
import {
  Container,
  Title,
  Text,
  Tabs,
  Group,
  Select,
  Badge,
  Card,
  SimpleGrid,
  Popover,
  Button,
  Indicator,
  List,
} from "@mantine/core";
import { rspcApi } from "../api/api";
import ResearchProposalManager from "./ResearchProposalManager";
import ConsultancyManager from "./ConsultancyManager";
import StaffAppointmentManager from "./StaffAppointmentManager";
import FinancialManagement from "./FinancialManagement";
import ProcurementManager from "./ProcurementManager";
import ReportsAndClosure from "./ReportsAndClosure";
import AuditLogViewer from "./AuditLogViewer";

export default function RSPCDashboard() {
  const [activeTab, setActiveTab] = useState<string | null>("proposals");
  const [userRole, setUserRole] = useState<string>("FACULTY");
  const [profile, setProfile] = useState<any>(null);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [stats, setStats] = useState({
    proposalsCount: 0,
    sanctionedTotal: 0,
    consultanciesCount: 0,
    pendingActions: 0,
  });

  const loadProfileAndStats = async () => {
    try {
      const p = await rspcApi.getProfile();
      setProfile(p);
      const savedRole = localStorage.getItem("rspc_active_role") || p.role || "FACULTY";
      setUserRole(savedRole);

      const [props, consults, fin, notifs] = await Promise.all([
        rspcApi.getProposals(),
        rspcApi.getConsultancies(),
        rspcApi.getFinancialRequests(),
        rspcApi.getNotifications(),
      ]);

      const sanctioned = props
        .filter((pr: any) => pr.is_sanctioned)
        .reduce((sum: number, pr: any) => sum + Number(pr.sanctioned_budget || 0), 0);

      const pending =
        props.filter((pr: any) => pr.status === "SUBMITTED" || pr.status === "ADMIN_VERIFIED").length +
        fin.filter((f: any) => f.status === "SUBMITTED" || f.status === "VERIFIED").length;

      setStats({
        proposalsCount: props.length,
        sanctionedTotal: sanctioned,
        consultanciesCount: consults.length,
        pendingActions: pending,
      });
      setNotifications(notifs);
    } catch {
      // Graceful fallback
    }
  };

  useEffect(() => {
    loadProfileAndStats();
  }, []);

  const handleRoleChange = async (newRole: string | null) => {
    if (!newRole) return;
    setUserRole(newRole);
    localStorage.setItem("rspc_active_role", newRole);
    try {
      await rspcApi.switchRole(newRole);
      loadProfileAndStats();
    } catch {
      // Offline fallback
    }
  };

  const handleMarkNotifRead = async (id: number) => {
    await rspcApi.markNotificationRead(id);
    loadProfileAndStats();
  };

  const unreadNotifs = notifications.filter((n) => !n.is_read);

  return (
    <Container size="xl" py="lg">
      {/* Top Header */}
      <Card withBorder p="md" mb="lg" radius="md">
        <Group justify="space-between" align="center">
          <div>
            <Group gap="xs">
              <Title order={2}>RSPC Management Portal</Title>
              <Badge size="lg" color="blue" variant="filled">IIITDM Jabalpur</Badge>
            </Group>
            <Text c="dimmed" size="sm">
              Research, Sponsored Projects & Consultancy ERP Subsystem | User: {profile?.username || "Faculty"} ({profile?.department || "CSE"})
            </Text>
          </div>

          <Group gap="md">
            {/* Active Actor Role Selector */}
            <Select
              label="Simulate Actor Role"
              size="xs"
              value={userRole}
              onChange={handleRoleChange}
              data={[
                { value: "FACULTY", label: "Faculty (PI / Co-PI)" },
                { value: "HOD", label: "Head of Department (HoD)" },
                { value: "RSPC_ADMIN", label: "RSPC Admin" },
                { value: "DEAN_RSPC", label: "Dean RSPC" },
                { value: "DIRECTOR", label: "Director" },
              ]}
              w={210}
            />

            {/* Notification Popover */}
            <Popover width={320} position="bottom-end" withArrow shadow="md">
              <Popover.Target>
                <Indicator label={unreadNotifs.length} size={16} disabled={unreadNotifs.length === 0} color="red">
                  <Button variant="light" size="xs">Notifications</Button>
                </Indicator>
              </Popover.Target>
              <Popover.Dropdown>
                <Title order={6} mb="xs">RSPC Notifications</Title>
                <List spacing="xs" size="xs">
                  {notifications.map((n) => (
                    <List.Item key={n.id}>
                      <Group justify="space-between" align="flex-start">
                        <div>
                          <Text fw={n.is_read ? 400 : 700}>{n.title}</Text>
                          <Text size="xs" c="dimmed">{n.message}</Text>
                        </div>
                        {!n.is_read && (
                          <Button size="compact-xs" variant="subtle" onClick={() => handleMarkNotifRead(n.id)}>
                            &check;
                          </Button>
                        )}
                      </Group>
                    </List.Item>
                  ))}
                  {notifications.length === 0 && (
                    <Text size="xs" c="dimmed">No notifications received.</Text>
                  )}
                </List>
              </Popover.Dropdown>
            </Popover>
          </Group>
        </Group>

        {/* Top KPI Summary Cards */}
        <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} mt="md">
          <Card withBorder padding="xs" radius="sm">
            <Text size="xs" c="dimmed" tt="uppercase" fw={700}>Research Proposals</Text>
            <Text size="xl" fw={700} c="blue">{stats.proposalsCount}</Text>
            <Text size="xs" c="dimmed">Total Grant Submissions</Text>
          </Card>
          <Card withBorder padding="xs" radius="sm">
            <Text size="xs" c="dimmed" tt="uppercase" fw={700}>Sanctioned Funding</Text>
            <Text size="xl" fw={700} c="green">₹{stats.sanctionedTotal.toLocaleString("en-IN")}</Text>
            <Text size="xs" c="dimmed">Active Project Grants</Text>
          </Card>
          <Card withBorder padding="xs" radius="sm">
            <Text size="xs" c="dimmed" tt="uppercase" fw={700}>Consultancies</Text>
            <Text size="xl" fw={700} c="cyan">{stats.consultanciesCount}</Text>
            <Text size="xs" c="dimmed">Industry Assignments</Text>
          </Card>
          <Card withBorder padding="xs" radius="sm">
            <Text size="xs" c="dimmed" tt="uppercase" fw={700}>Pending Actions</Text>
            <Text size="xl" fw={700} c="orange">{stats.pendingActions}</Text>
            <Text size="xs" c="dimmed">Awaiting Review/Sanction</Text>
          </Card>
        </SimpleGrid>
      </Card>

      {/* Main Tabs Navigation */}
      <Tabs value={activeTab} onChange={setActiveTab}>
        <Tabs.List mb="md">
          <Tabs.Tab value="proposals">Research Proposals (CW-01)</Tabs.Tab>
          <Tabs.Tab value="consultancy">Consultancy Projects (CW-02)</Tabs.Tab>
          <Tabs.Tab value="staff">Staff Appointments (CW-03)</Tabs.Tab>
          <Tabs.Tab value="finance">Financial Management (CW-04)</Tabs.Tab>
          <Tabs.Tab value="procurement">Procurement (CW-05)</Tabs.Tab>
          <Tabs.Tab value="reports">Reports & Closure (CW-06)</Tabs.Tab>
          <Tabs.Tab value="audit">Audit Logs (BR-050)</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="proposals">
          <ResearchProposalManager userRole={userRole} />
        </Tabs.Panel>

        <Tabs.Panel value="consultancy">
          <ConsultancyManager userRole={userRole} />
        </Tabs.Panel>

        <Tabs.Panel value="staff">
          <StaffAppointmentManager userRole={userRole} />
        </Tabs.Panel>

        <Tabs.Panel value="finance">
          <FinancialManagement userRole={userRole} />
        </Tabs.Panel>

        <Tabs.Panel value="procurement">
          <ProcurementManager userRole={userRole} />
        </Tabs.Panel>

        <Tabs.Panel value="reports">
          <ReportsAndClosure userRole={userRole} />
        </Tabs.Panel>

        <Tabs.Panel value="audit">
          <AuditLogViewer />
        </Tabs.Panel>
      </Tabs>
    </Container>
  );
}
