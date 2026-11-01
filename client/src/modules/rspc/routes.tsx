import type { RouteObject } from "react-router-dom";
import RSPCDashboard from "./pages/RSPCDashboard";

export const routes: RouteObject[] = [
  { index: true, element: <RSPCDashboard /> },
  { path: "*", element: <RSPCDashboard /> },
];

export default function RSPCRoutes() {
  return <RSPCDashboard />;
}
