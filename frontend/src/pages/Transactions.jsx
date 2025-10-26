import { useEffect, useState } from "react";
import { deleteTransaction } from "../services/transactions";
import api from "../services/api";
import toast from "react-hot-toast";

export default function EnhancedTransactions() {
  const [transactions, setTransactions] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  
  // Filter states
  const [filters, setFilters] = useState({
    type: "all",
    accountUid: "all",
    categoryUid: "all",
    dateFrom: "",
    dateTo: "",
    minAmount: "",
    maxAmount: "",
    searchTerm: ""
  });
  
  // View preferences
  const [viewMode, setViewMode] = useState("table"); // table or cards
  const [sortBy, setSortBy] = useState("date-desc");
  const [showSummary, setShowSummary] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [txRes, accRes, catRes] = await Promise.all([
        api.get("/transactions/"),
        api.get("/accounts/"),
        api.get("/categories/"),
      ]);
      setTransactions(txRes.data);
      setAccounts(accRes.data);
      setCategories(catRes.data);
    } catch (err) {
      console.error("Error fetching data:", err);
      toast.error("Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (uid) => {
    if (!confirm("Delete this transaction?")) return;
    try {
      await deleteTransaction(uid);
      setTransactions((prev) => prev.filter((tx) => tx.uid !== uid));
      toast.success("Transaction deleted");
    } catch (err) {
      toast.error("Failed to delete transaction");
    }
  };

  // Apply filters
  const filteredTransactions = transactions.filter(tx => {
    // Type filter
    if (filters.type !== "all" && tx.type !== filters.type) return false;
    
    // Account filter
    if (filters.accountUid !== "all") {
      const matchAccount = tx.account_uid === filters.accountUid ||
        tx.from_account_uid === filters.accountUid ||
        tx.to_account_uid === filters.accountUid;
      if (!matchAccount) return false;
    }
    
    // Category filter
    if (filters.categoryUid !== "all" && tx.category_uid !== filters.categoryUid) return false;
    
    // Date range
    const txDate = new Date(tx.date);
    if (filters.dateFrom && txDate < new Date(filters.dateFrom)) return false;
    if (filters.dateTo && txDate > new Date(filters.dateTo)) return false;
    
    // Amount range
    if (filters.minAmount && tx.amount < parseFloat(filters.minAmount)) return false;
    if (filters.maxAmount && tx.amount > parseFloat(filters.maxAmount)) return false;
    
    // Search term
    if (filters.searchTerm) {
      const term = filters.searchTerm.toLowerCase();
      const searchableText = `${tx.description || ""} ${tx.account_name || ""} ${tx.category_name || ""}`.toLowerCase();
      if (!searchableText.includes(term)) return false;
    }
    
    return true;
  });

  // Sort transactions
  const sortedTransactions = [...filteredTransactions].sort((a, b) => {
    switch (sortBy) {
      case "date-desc": return new Date(b.date) - new Date(a.date);
      case "date-asc": return new Date(a.date) - new Date(b.date);
      case "amount-desc": return b.amount - a.amount;
      case "amount-asc": return a.amount - b.amount;
      default: return 0;
    }
  });

  // Calculate running summary
  const summary = sortedTransactions.reduce((acc, tx) => {
    if (tx.type === "income") {
      acc.totalIncome += tx.amount;
      acc.count.income++;
    } else if (tx.type === "expense") {
      acc.totalExpense += tx.amount;
      acc.count.expense++;
    } else if (tx.type === "transfer") {
      acc.count.transfer++;
    }
    return acc;
  }, {
    totalIncome: 0,
    totalExpense: 0,
    count: { income: 0, expense: 0, transfer: 0 },
    netAmount: 0
  });
  
  summary.netAmount = summary.totalIncome - summary.totalExpense;

  // Calculate running balance
  let runningBalance = 0;
  const transactionsWithBalance = sortedTransactions.map(tx => {
    if (tx.type === "income") {
      runningBalance += tx.amount;
    } else if (tx.type === "expense") {
      runningBalance -= tx.amount;
    }
    return { ...tx, runningBalance };
  });

  const clearFilters = () => {
    setFilters({
      type: "all",
      accountUid: "all",
      categoryUid: "all",
      dateFrom: "",
      dateTo: "",
      minAmount: "",
      maxAmount: "",
      searchTerm: ""
    });
  };

  const activeFilterCount = Object.values(filters).filter(v => v && v !== "all").length;

  if (loading) {
    return <div className="p-6 text-center text-gray-500">Loading...</div>;
  }

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">💳 Transactions</h1>
          <p className="text-gray-600 mt-1">
            {filteredTransactions.length} of {transactions.length} transactions
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowSummary(!showSummary)}
            className="px-4 py-2 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            {showSummary ? "📊 Hide" : "📊 Show"} Summary
          </button>
          <button
            onClick={() => setShowForm(true)}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors shadow-md"
          >
            + Add Transaction
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      {showSummary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-2xl">💰</span>
              <span className="text-xs font-medium text-green-600">{summary.count.income} txns</span>
            </div>
            <p className="text-sm text-gray-600 mb-1">Total Income</p>
            <p className="text-2xl font-bold text-green-700">₱{summary.totalIncome.toLocaleString()}</p>
          </div>
          
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-2xl">💸</span>
              <span className="text-xs font-medium text-red-600">{summary.count.expense} txns</span>
            </div>
            <p className="text-sm text-gray-600 mb-1">Total Expense</p>
            <p className="text-2xl font-bold text-red-700">₱{summary.totalExpense.toLocaleString()}</p>
          </div>
          
          <div className={`border rounded-lg p-4 ${summary.netAmount >= 0 ? 'bg-blue-50 border-blue-200' : 'bg-orange-50 border-orange-200'}`}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-2xl">{summary.netAmount >= 0 ? '📈' : '📉'}</span>
              <span className="text-xs font-medium text-gray-600">{summary.count.transfer} transfers</span>
            </div>
            <p className="text-sm text-gray-600 mb-1">Net Amount</p>
            <p className={`text-2xl font-bold ${summary.netAmount >= 0 ? 'text-blue-700' : 'text-orange-700'}`}>
              ₱{summary.netAmount.toLocaleString()}
            </p>
          </div>
          
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-2xl">📊</span>
              <span className="text-xs font-medium text-purple-600">Average</span>
            </div>
            <p className="text-sm text-gray-600 mb-1">Per Transaction</p>
            <p className="text-2xl font-bold text-purple-700">
              ₱{filteredTransactions.length ? (summary.totalExpense / summary.count.expense || 0).toLocaleString(undefined, {maximumFractionDigits: 0}) : 0}
            </p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md border p-4 space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="font-semibold text-gray-800 flex items-center gap-2">
            🔍 Filters
            {activeFilterCount > 0 && (
              <span className="bg-blue-600 text-white text-xs px-2 py-1 rounded-full">
                {activeFilterCount}
              </span>
            )}
          </h3>
          {activeFilterCount > 0 && (
            <button
              onClick={clearFilters}
              className="text-sm text-blue-600 hover:underline"
            >
              Clear all
            </button>
          )}
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {/* Search */}
          <div className="md:col-span-2">
            <input
              type="text"
              placeholder="🔍 Search description, account, category..."
              value={filters.searchTerm}
              onChange={(e) => setFilters({...filters, searchTerm: e.target.value})}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            />
          </div>
          
          {/* Type */}
          <select
            value={filters.type}
            onChange={(e) => setFilters({...filters, type: e.target.value})}
            className="border rounded-lg px-3 py-2 text-sm"
          >
            <option value="all">All Types</option>
            <option value="income">Income</option>
            <option value="expense">Expense</option>
            <option value="transfer">Transfer</option>
            <option value="reimburse">Reimburse</option>
          </select>
          
          {/* Account */}
          <select
            value={filters.accountUid}
            onChange={(e) => setFilters({...filters, accountUid: e.target.value})}
            className="border rounded-lg px-3 py-2 text-sm"
          >
            <option value="all">All Accounts</option>
            {accounts.map(acc => (
              <option key={acc.uid} value={acc.uid}>{acc.name}</option>
            ))}
          </select>
          
          {/* Category */}
          <select
            value={filters.categoryUid}
            onChange={(e) => setFilters({...filters, categoryUid: e.target.value})}
            className="border rounded-lg px-3 py-2 text-sm"
          >
            <option value="all">All Categories</option>
            {categories.map(cat => (
              <option key={cat.uid} value={cat.uid}>{cat.name}</option>
            ))}
          </select>
          
          {/* Date From */}
          <div>
            <input
              type="date"
              value={filters.dateFrom}
              onChange={(e) => setFilters({...filters, dateFrom: e.target.value})}
              className="w-full border rounded-lg px-3 py-2 text-sm"
              placeholder="From date"
            />
          </div>
          
          {/* Date To */}
          <div>
            <input
              type="date"
              value={filters.dateTo}
              onChange={(e) => setFilters({...filters, dateTo: e.target.value})}
              className="w-full border rounded-lg px-3 py-2 text-sm"
              placeholder="To date"
            />
          </div>
          
          {/* Min Amount */}
          <input
            type="number"
            placeholder="Min amount"
            value={filters.minAmount}
            onChange={(e) => setFilters({...filters, minAmount: e.target.value})}
            className="border rounded-lg px-3 py-2 text-sm"
          />
          
          {/* Max Amount */}
          <input
            type="number"
            placeholder="Max amount"
            value={filters.maxAmount}
            onChange={(e) => setFilters({...filters, maxAmount: e.target.value})}
            className="border rounded-lg px-3 py-2 text-sm"
          />
        </div>
      </div>

      {/* View Controls */}
      <div className="flex justify-between items-center">
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode("table")}
            className={`px-4 py-2 rounded-lg transition-colors ${viewMode === "table" ? "bg-blue-600 text-white" : "bg-white border hover:bg-gray-50"}`}
          >
            📋 Table
          </button>
          <button
            onClick={() => setViewMode("cards")}
            className={`px-4 py-2 rounded-lg transition-colors ${viewMode === "cards" ? "bg-blue-600 text-white" : "bg-white border hover:bg-gray-50"}`}
          >
            🗂️ Cards
          </button>
        </div>
        
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm"
        >
          <option value="date-desc">📅 Newest First</option>
          <option value="date-asc">📅 Oldest First</option>
          <option value="amount-desc">💰 Highest Amount</option>
          <option value="amount-asc">💰 Lowest Amount</option>
        </select>
      </div>

      {/* Transactions Display */}
      {sortedTransactions.length === 0 ? (
        <div className="bg-white rounded-lg p-12 text-center border shadow-sm">
          <div className="text-6xl mb-4">💳</div>
          <p className="text-lg font-medium text-gray-700 mb-2">No Transactions Found</p>
          <p className="text-gray-500">Try adjusting your filters or add a new transaction</p>
        </div>
      ) : viewMode === "table" ? (
        <div className="bg-white rounded-lg shadow-md border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-3 text-left font-semibold">Date</th>
                  <th className="px-4 py-3 text-left font-semibold">Type</th>
                  <th className="px-4 py-3 text-left font-semibold">Account</th>
                  <th className="px-4 py-3 text-left font-semibold">Category</th>
                  <th className="px-4 py-3 text-right font-semibold">Amount</th>
                  <th className="px-4 py-3 text-right font-semibold">Running Balance</th>
                  <th className="px-4 py-3 text-left font-semibold">Description</th>
                  <th className="px-4 py-3 text-center font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody>
                {transactionsWithBalance.map((tx) => (
                  <tr key={tx.uid} className="border-b hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 whitespace-nowrap">
                      {new Date(tx.date).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        tx.type === "income" ? "bg-green-100 text-green-700" :
                        tx.type === "expense" ? "bg-red-100 text-red-700" :
                        tx.type === "transfer" ? "bg-blue-100 text-blue-700" :
                        "bg-purple-100 text-purple-700"
                      }`}>
                        {tx.type}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {tx.account_name || tx.from_account_name || "—"}
                    </td>
                    <td className="px-4 py-3">
                      {tx.category_name || tx.to_account_name || "—"}
                    </td>
                    <td className={`px-4 py-3 text-right font-semibold ${
                      tx.type === "expense" ? "text-red-600" :
                      tx.type === "income" ? "text-green-600" :
                      "text-blue-600"
                    }`}>
                      ₱{tx.amount.toLocaleString()}
                    </td>
                    <td className={`px-4 py-3 text-right font-semibold ${
                      tx.runningBalance >= 0 ? "text-green-600" : "text-red-600"
                    }`}>
                      ₱{tx.runningBalance.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 max-w-xs truncate">
                      {tx.description || "—"}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => handleDelete(tx.uid)}
                        className="text-red-600 hover:text-red-800 font-medium"
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {transactionsWithBalance.map((tx) => (
            <div key={tx.uid} className="bg-white rounded-lg shadow-md border p-4 hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-3">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  tx.type === "income" ? "bg-green-100 text-green-700" :
                  tx.type === "expense" ? "bg-red-100 text-red-700" :
                  tx.type === "transfer" ? "bg-blue-100 text-blue-700" :
                  "bg-purple-100 text-purple-700"
                }`}>
                  {tx.type}
                </span>
                <button
                  onClick={() => handleDelete(tx.uid)}
                  className="text-red-600 hover:text-red-800"
                >
                  🗑️
                </button>
              </div>
              
              <p className={`text-2xl font-bold mb-2 ${
                tx.type === "expense" ? "text-red-600" :
                tx.type === "income" ? "text-green-600" :
                "text-blue-600"
              }`}>
                ₱{tx.amount.toLocaleString()}
              </p>
              
              <p className="text-sm text-gray-600 mb-1">
                📅 {new Date(tx.date).toLocaleDateString()}
              </p>
              
              {tx.account_name && (
                <p className="text-sm text-gray-600 mb-1">
                  🏦 {tx.account_name}
                </p>
              )}
              
              {tx.category_name && (
                <p className="text-sm text-gray-600 mb-1">
                  📂 {tx.category_name}
                </p>
              )}
              
              {tx.description && (
                <p className="text-sm text-gray-700 mt-2 italic">
                  "{tx.description}"
                </p>
              )}
              
              <div className="mt-3 pt-3 border-t">
                <p className="text-xs text-gray-500">Running Balance</p>
                <p className={`text-lg font-semibold ${
                  tx.runningBalance >= 0 ? "text-green-600" : "text-red-600"
                }`}>
                  ₱{tx.runningBalance.toLocaleString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Export Button */}
      <div className="flex justify-center">
        <button
          onClick={() => {
            const csv = [
              ["Date", "Type", "Account", "Category", "Amount", "Running Balance", "Description"],
              ...transactionsWithBalance.map(tx => [
                new Date(tx.date).toLocaleDateString(),
                tx.type,
                tx.account_name || tx.from_account_name || "",
                tx.category_name || tx.to_account_name || "",
                tx.amount,
                tx.runningBalance,
                tx.description || ""
              ])
            ].map(row => row.join(",")).join("\n");
            
            const blob = new Blob([csv], { type: "text/csv" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `transactions-${new Date().toISOString().split("T")[0]}.csv`;
            a.click();
            toast.success("Exported to CSV");
          }}
          className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors shadow-md"
        >
          📥 Export to CSV
        </button>
      </div>
    </div>
  );
}