import type { ReactNode } from "react";
import type { WorkspaceRole } from "../../shared/api";

export type Screen = "dashboard" | "employees" | "insights" | "settings";
type SidebarProps = { screen: Screen; role: WorkspaceRole; onChange: (screen: Screen) => void };

function Nav({ active, onClick, children }: { active: boolean; onClick: () => void; children: ReactNode }) {
  return <button className={`nav ${active ? "active" : ""}`} onClick={onClick}>{children}</button>;
}

export default function Sidebar({ screen, role, onChange }: SidebarProps) {
  const isAdmin = role === "ADMIN";
  return <aside><div className="brand">ACME <span>Comp Hub</span></div><div className="nav-label">Workspace</div><Nav active={screen === "dashboard"} onClick={() => onChange("dashboard")}>▦ &nbsp; Dashboard</Nav><Nav active={screen === "employees"} onClick={() => onChange("employees")}>⌕ &nbsp; Employees</Nav><Nav active={screen === "insights"} onClick={() => onChange("insights")}>◒ &nbsp; Insights</Nav>{isAdmin && <><div className="nav-label">Manage</div><Nav active={screen === "settings"} onClick={() => onChange("settings")}>⚙ &nbsp; Admin settings</Nav></>}<div className="sidebar-note"><b>{isAdmin ? "Administrator access" : "Internal HR workspace"}</b><span>{isAdmin ? "You can manage HR users and roles." : "Compensation data is visible to authorized HR users only."}</span></div></aside>;
}
