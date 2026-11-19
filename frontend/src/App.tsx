import { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import Sidebar, { type Screen } from "./components/Sidebar";
import Topbar from "./components/Topbar";
import MobileNavigation from "./components/MobileNavigation";
import Login from "./pages/Login";
import DashboardPage from "./pages/Dashboard";
import EmployeesPage, { ProfileDrawer } from "./pages/Employees";
import InsightsPage from "./pages/Insights";
import AdminSettingsPage from "./pages/AdminSettings";
import { api, type AuthUser } from "./shared/api";

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem("acme_token"));
  const queryClient = useQueryClient();
  const session = useQuery({ queryKey: ["me", token], queryFn: () => api<AuthUser>("/api/auth/me"), enabled: Boolean(token), retry: false });
  useEffect(() => {
    if (session.isError) localStorage.removeItem("acme_token");
  }, [session.isError]);
  if (!token || session.isError) return <Login onLogin={(nextToken, nextUser) => {
    localStorage.setItem("acme_token", nextToken);
    queryClient.setQueryData(["me", nextToken], nextUser);
    setToken(nextToken);
  }} />;
  if (!session.data) return <div className="state" role="status">Checking your session…</div>;
  return <AuthenticatedApp user={session.data} onLogout={() => {
    void api("/api/auth/logout", { method: "POST" }).catch(() => undefined);
    localStorage.removeItem("acme_token");
    queryClient.clear();
    setToken(null);
  }} />;
}

function AuthenticatedApp({ user, onLogout }: { user: AuthUser; onLogout: () => void }) {
  const queryClient = useQueryClient();
  const [screen, setScreen] = useState<Screen>("dashboard");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [search, setSearch] = useState("");
  const [country, setCountry] = useState("");
  const [department, setDepartment] = useState("");
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);
  const [sort, setSort] = useState("name");
  const [direction, setDirection] = useState<"asc" | "desc">("asc");
  const logout = () => { queryClient.clear(); onLogout(); };
  const updateSearch = (value: string) => { setSearch(value); setPage(1); };
  const updateCountry = (value: string) => { setCountry(value); setPage(1); };
  const updateDepartment = (value: string) => { setDepartment(value); setPage(1); };
  const updateStatus = (value: string) => { setStatus(value); setPage(1); };
  const updateSort = (column: string) => {
    if (sort === column) setDirection(direction === "asc" ? "desc" : "asc");
    else { setSort(column); setDirection("asc"); }
    setPage(1);
  };

  return <div className="app-shell">
    <Sidebar screen={screen} role={user.role} onChange={setScreen} />
    <main>
      <Topbar screen={screen} user={user} onLogout={logout} />
      <div className={`content ${screen === "employees" ? "directory-content" : ""}`}>
        {screen === "dashboard" && <DashboardPage name={user.name} onViewEmployees={() => setScreen("employees")} />}
        {screen === "employees" && <EmployeesPage search={search} setSearch={updateSearch} country={country} setCountry={updateCountry} department={department} setDepartment={updateDepartment} status={status} setStatus={updateStatus} page={page} setPage={setPage} sort={sort} direction={direction} onSort={updateSort} onSelect={setSelectedId} />}
        {screen === "insights" && <InsightsPage />}
        {screen === "settings" && user.role === "ADMIN" && <AdminSettingsPage currentUserId={user.id} onLogout={logout} />}
      </div>
    </main>
    <MobileNavigation screen={screen} role={user.role} onChange={setScreen} />
    {selectedId && <ProfileDrawer id={selectedId} onClose={() => setSelectedId(null)} />}
  </div>;
}
