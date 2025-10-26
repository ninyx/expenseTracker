// frontend/src/pages/Dashboard.jsx
import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { getAccounts, getTransactions, getCategories } from "../services/dashboard";

// Import the enhanced components
import { CategoryBudgets } from "../components/dashboard/CategoryBudgets.jsx";
import { SummaryCards } from "../components/dashboard/SummaryCards.jsx";
import { DashboardCharts } from "../components/dashboard/DashboardCharts.jsx";
import { TransactionsList } from "../components/dashboard/TransactionList.jsx";

export default function Dashboard() {
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [totals, setTotals] = useState({ income: 0, expense: 0, balance: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        setLoading(true);
        const [accData, txData, catData] = await Promise.all([
          getAccounts(),
          getTransactions(),
          getCategories(),
        ]);

        console.log("Accounts:", accData);
        console.log("Transactions:", txData);
        console.log("Categories:", catData);

        // Ensure arrays
        const acc = Array.isArray(accData) ? accData : [];
        const tx = Array.isArray(txData) ? txData : [];
        const cat = Array.isArray(catData) ? catData : [];

        setAccounts(acc);
        setCategories(cat);

        // Sort transactions by date descending and take latest 10
        const latestTx = tx
          .slice()
          .sort((a, b) => new Date(b.date) - new Date(a.date))
          .slice(0, 10);

        setTransactions(latestTx);

        // Totals calculation (ensure numbers)
        const income = tx
          .filter((t) => t.transaction_type === "income")
          .reduce((sum, t) => sum + Number(t.amount || 0), 0);

        const expense = tx
          .filter((t) => t.transaction_type === "expense")
          .reduce((sum, t) => sum + Number(t.amount || 0), 0);

        const balance = acc
          .reduce((sum, a) => sum + Number(a.balance || 0), 0);

        setTotals({ income, expense, balance });

      } catch (err) {
        console.error("Dashboard fetch error:", err);
        toast.error("Failed to load dashboard");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">⏳</div>
          <p className="text-gray-500 text-lg">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">📊 Dashboard</h1>
          <p className="text-gray-600">Overview of your financial health</p>
        </div>
        
        <SummaryCards totals={totals} />
        <DashboardCharts totals={totals} categories={categories} accounts={accounts} />
        <TransactionsList
          transactions={transactions}
          accounts={accounts}
          categories={categories}
        />
        <CategoryBudgets categories={categories} />
      </div>
    </div>
  );
}