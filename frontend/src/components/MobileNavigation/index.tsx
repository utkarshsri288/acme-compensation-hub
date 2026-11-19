import type { Screen } from "../Sidebar";
import type { WorkspaceRole } from "../../shared/api";
import "./styles.css";

type Props = { screen: Screen; role: WorkspaceRole; onChange: (screen: Screen) => void };

export default function MobileNavigation({ screen, role, onChange }: Props) {
  const items: { screen: Screen; label: string }[] = [
    { screen: "dashboard", label: "Dashboard" },
    { screen: "employees", label: "Employees" },
    { screen: "insights", label: "Insights" },
    ...(role === "ADMIN" ? [{ screen: "settings" as Screen, label: "Settings" }] : []),
  ];
  return <nav className="mobile-navigation" aria-label="Mobile navigation">
    {items.map(item => <button key={item.screen} type="button" className={screen === item.screen ? "active" : ""}
      aria-current={screen === item.screen ? "page" : undefined} onClick={() => onChange(item.screen)}>{item.label}</button>)}
  </nav>;
}
