// src/components/Sidebar.jsx - Debug version
import { useState } from "react";
import { Link, useLocation, Outlet } from "react-router";

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  console.log("Sidebar rendered, current path:", location.pathname);

  const linkClass = (path) =>
    `flex items-center gap-3 px-4 py-2 rounded-md transition-all duration-200
    ${location.pathname === path
      ? "bg-blue-500 text-white"
      : "text-gray-700 hover:bg-gray-100 hover:text-blue-600"}`;

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside
        className={`bg-white border-r shadow-sm transition-all duration-300
          ${collapsed ? "w-16" : "w-60"}`}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          {!collapsed && <h1 className="text-lg font-bold text-blue-600">💰 Expense Tracker</h1>}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="text-gray-500 hover:text-blue-600 text-xl"
            title={collapsed ? "Expand" : "Collapse"}
          >
            {collapsed ? "☰" : "×"}
          </button>
        </div>

        {/* Nav Links */}
        <nav className="flex flex-col gap-1 p-4">
          <Link to="/" className={linkClass("/")}>
            <span className="text-xl">📊</span>
            {!collapsed && <span>Dashboard</span>}
          </Link>

          <Link to="/accounts" className={linkClass("/accounts")}>
            <span className="text-xl">🏦</span>
            {!collapsed && <span>Accounts</span>}
          </Link>

          <Link to="/transactions" className={linkClass("/transactions")}>
            <span className="text-xl">💸</span>
            {!collapsed && <span>Transactions</span>}
          </Link>

          <Link to="/categories" className={linkClass("/categories")}>
            <span className="text-xl">📂</span>
            {!collapsed && <span>Categories</span>}
          </Link>

          <Link to="/budget" className={linkClass("/budget")}>
            <span className="text-xl">📅</span>
            {!collapsed && <span>Budget Tracker</span>}
          </Link>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 bg-gray-50 p-6 overflow-y-auto">
        
        {/* This is where child routes render */}
        <Outlet />
        
      </main>
    </div>
  );
}