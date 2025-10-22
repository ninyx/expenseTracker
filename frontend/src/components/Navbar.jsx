import { Link, useLocation } from "react-router";

export default function Navbar() {
  const location = useLocation();
  const linkClass = (path) =>
    `px-4 py-2 rounded-md ${location.pathname === path ? "bg-blue-500 text-white" : "hover:bg-gray-100"}`;

  return (
    <nav className="flex space-x-4 border-b p-4 bg-white shadow-sm">
      <Link to="/" className={linkClass("/")}>Dashboard</Link>
      <Link to="/accounts" className={linkClass("/accounts")}>Accounts</Link>
      <Link to="/transactions" className={linkClass("/transactions")}>Transactions</Link>
      <Link to="/categories" className={linkClass("/categories")}>Categories</Link>
    </nav>
  );
}
