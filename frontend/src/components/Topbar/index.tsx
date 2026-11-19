import Button from "../Button";
import type { Screen } from "../Sidebar";

type TopbarProps = { screen: Screen; user: { name: string }; onLogout: () => void };

export default function Topbar({ screen, user, onLogout }: TopbarProps) {
  const title = screen === "dashboard" ? "Dashboard" : screen === "employees" ? "Employee directory" : screen === "insights" ? "Compensation insights" : "Admin settings";
  return <header><b>{title}</b><span>{user.name} <i>{user.name.split(" ").map(part => part[0]).join("").slice(0, 2)}</i><Button className="logout" onClick={onLogout}>Log out</Button></span></header>;
}
