// src/App.jsx - Complete working example
import { BrowserRouter, Routes, Route } from "react-router";
import Sidebar from "./components/Sidebar";

import Budget from "./pages/BudgetTracker.jsx";
import Categories from "./pages/Categories.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Accounts from "./pages/Accounts.jsx";
import Transactions from "./pages/Transactions.jsx";

export default function App() {
  return (
    <Routes>
      {/* Sidebar wraps all routes as the layout */}
      <Route path="/" element={<Sidebar />}>
        {/* These routes render inside the <Outlet /> */}
        <Route index element={<Dashboard />} />
        <Route path="accounts" element={<Accounts />} />
        <Route path="transactions" element={<Transactions />} />
        <Route path="categories" element={<Categories />} />
        <Route path="budget" element={<Budget />} />
      </Route>
    </Routes>
  );
}