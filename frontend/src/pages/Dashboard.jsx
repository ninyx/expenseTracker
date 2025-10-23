import React, { useEffect, useState } from "react";
import { getAccounts, getTransactions, getCategories } from "../services/dashboard";
import toast from "react-hot-toast";

export default function Dashboard() {
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [totals, setTotals] = useState({
    income: 0,
    expense: 0,
    reimburse: 0,
    balance: 0,
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [accData, txData, catData] = await Promise.all([
        getAccounts(),
        getTransactions(),
        getCategories(),
      ]);

      // Sort transactions by date (latest first)
      const sortedTx = txData.sort((a, b) => new Date(b.date) - new Date(a.date));
      setTransactions(sortedTx.slice(0, 10)); // only 10 latest

      setAccounts(accData);
      setCategories(catData);

      const totalIncome = txData
        .filter((t) => t.transaction_type === "income")
        .reduce((sum, t) => sum + (t.amount || 0), 0);

      const totalExpense = txData
        .filter((t) => t.transaction_type === "expense")
        .reduce((sum, t) => sum + (t.amount || 0), 0);

      const totalReimburse = txData
        .filter((t) => t.transaction_type === "reimburse")
        .reduce((sum, t) => sum + (t.amount || 0), 0);

      const totalBalance = accData.reduce(
        (sum, a) => sum + (a.balance || 0),
        0
      );

      setTotals({
        income: totalIncome,
        expense: totalExpense,
        reimburse: totalReimburse,
        balance: totalBalance,
      });
    } catch (err) {
      console.error("Error loading dashboard data:", err);
      toast.error("Failed to load dashboard");
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">📊 Dashboard</h1>

      {/* SUMMARY CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
        <SummaryCard label="Total Income" value={totals.income} color="text-green-600" />
        <SummaryCard label="Total Expense" value={totals.expense} color="text-red-600" />
        {totals.reimburse > 0 && (
          <SummaryCard label="Total Reimbursements" value={totals.reimburse} color="text-amber-600" />
        )}
        <SummaryCard label="Total Balance" value={totals.balance} color="text-blue-600" />
      </div>

      {/* RECENT TRANSACTIONS */}
      <div className="mt-6">
        <h2 className="text-lg font-semibold mb-2">Recent Transactions (Latest 10)</h2>
        <div className="bg-white rounded shadow p-4">
          {transactions.length === 0 ? (
            <p className="text-gray-500 text-sm">No recent transactions.</p>
          ) : (
            transactions.map((tx) => (
              <TransactionItem
                key={tx.uid}
                tx={tx}
                accounts={accounts}
                categories={categories}
              />
            ))
          )}
        </div>
      </div>

      {/* CATEGORY BUDGET SNAPSHOT */}
      <div>
        <h2 className="text-lg font-semibold mb-2">Budget Overview</h2>
        <div className="border rounded p-3 bg-white shadow-sm">
          {categories.length === 0 ? (
            <p className="text-gray-500">No categories yet.</p>
          ) : (
            <div className="space-y-2">
              {categories.map((cat) => (
                <CategoryBudget key={cat.uid} category={cat} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function SummaryCard({ label, value, color }) {
  return (
    <div className="bg-white p-4 rounded shadow-sm border">
      <p className="text-gray-500 text-sm">{label}</p>
      <p className={`text-xl font-bold ${color}`}>₱{value.toLocaleString()}</p>
    </div>
  );
}

/* Transaction Item (expandable) */
function TransactionItem({ tx, accounts, categories }) {
  const [expanded, setExpanded] = useState(false);

  const account = accounts.find((a) => a.uid === tx.account_uid);
  const category = categories.find((c) => c.uid === tx.category_uid);

  // Define consistent type colors
  const typeColors = {
    income: {
      bg: "bg-green-100",
      text: "text-green-700",
      amount: "text-green-600",
      icon: "💰",
    },
    expense: {
      bg: "bg-red-100",
      text: "text-red-700",
      amount: "text-red-600",
      icon: "🛒",
    },
    reimburse: {
      bg: "bg-amber-100",
      text: "text-amber-700",
      amount: "text-amber-600",
      icon: "💵",
    },
    transfer: {
      bg: "bg-blue-100",
      text: "text-blue-700",
      amount: "text-blue-600",
      icon: "🔁",
    },
  };

  const txType = tx.transaction_type || tx.type || "other";
  const colors = typeColors[txType] || {
    bg: "bg-gray-100",
    text: "text-gray-700",
    amount: "text-gray-600",
    icon: "💼",
  };

  return (
    <div
      className="border-b py-3 last:border-none cursor-pointer hover:bg-gray-50 transition-colors rounded-sm"
      onClick={() => setExpanded(!expanded)}
    >
      {/* Top Line */}
      <div className="flex justify-between items-center">
        <div className="flex flex-col">
          <p className="font-medium flex items-center gap-1">
            <span>{colors.icon}</span> {tx.description || tx.name}
          </p>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span>{new Date(tx.date).toLocaleDateString()}</span>
            <span
              className={`font-semibold px-2 py-0.5 rounded-full ${colors.bg} ${colors.text}`}
            >
              {txType}
            </span>
          </div>
        </div>

        {/* Amount */}
        <p className={`font-semibold ${colors.amount}`}>
          ₱{tx.amount?.toLocaleString() ?? "0.00"}
        </p>
      </div>

      {/* Expanded Details */}
      {expanded && (
        <div className="text-xs text-gray-700 mt-2 ml-2 space-y-1 border-l-2 border-gray-200 pl-3">
          {account && (
            <p>
              💳 <span className="font-medium">{account.name}</span>
            </p>
          )}
          {category && (
            <p>
              🗂 <span className="font-medium">{category.name}</span>
            </p>
          )}
          {tx.transfer_fee && tx.transfer_fee > 0 && (
            <p>💸 Transfer Fee: ₱{tx.transfer_fee.toLocaleString()}</p>
          )}
          {tx.notes && <p>📝 {tx.notes}</p>}
        </div>
      )}
    </div>
  );
}


/* Category Budget Overview */
function CategoryBudget({ category }) {
  const usage = category.budget > 0 ? category.budget_used / category.budget : 0;
  const pct = Math.min(usage * 100, 100).toFixed(1);
  const color =
    usage > 1 ? "bg-red-500" : usage > 0.7 ? "bg-yellow-400" : "bg-green-500";

  return (
    <div>
      <div className="flex justify-between">
        <span>{category.name}</span>
        <span className="text-sm text-gray-500">
          ₱{category.budget_used?.toLocaleString() || 0} / ₱
          {category.budget?.toLocaleString() || 0} ({pct}%)
        </span>
      </div>
      <div className="h-2 bg-gray-200 rounded mt-1">
        <div className={`h-2 ${color} rounded`} style={{ width: `${pct}%` }}></div>
      </div>

      {category.children?.length > 0 && (
        <div className="ml-4 mt-2 space-y-1">
          {category.children.map((child) => (
            <CategoryBudget key={child.uid} category={child} />
          ))}
        </div>
      )}
    </div>
  );
}
