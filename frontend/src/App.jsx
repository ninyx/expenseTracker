// frontend/src/App.jsx
import { Routes, Route } from "react-router";
import Dashboard from "./pages/Dashboard";
import Accounts from "./pages/Accounts";
import Transactions from "./pages/Transactions";
import Categories from "./pages/Categories";
import Budget from "./pages/BudgetTracker.jsx";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar.jsx";

export default function App() {
  return (
    <div className="p-6">
      <Sidebar   />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/accounts" element={<Accounts />} />
        <Route path="/transactions" element={<Transactions />} />
        <Route path="/categories" element={<Categories />} />
        <Route path="/budget" element={<Budget />} />
      </Routes>
    </div>
  );
}