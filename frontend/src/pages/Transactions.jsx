import { useEffect, useState } from "react";
import { deleteTransaction } from "../services/transactions";
import api from "../services/api";
import toast from "react-hot-toast";
import TransactionForm from "../components/TransactionsForm.jsx";

export default function EnhancedTransactions() {
  const [transactions, setTransactions] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [showImport, setShowImport] = useState(false);
  
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
  const [viewMode, setViewMode] = useState("table");
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

  const handleImportCSV = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      toast.error("Please select a CSV file");
      return;
    }

    try {
      const text = await file.text();
      const lines = text.split('\n').filter(line => line.trim());
      
      if (lines.length < 2) {
        toast.error("CSV file is empty or invalid");
        return;
      }

      // Parse header
      const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
      
      // Expected headers: date, type, amount, description, account, category, from_account, to_account, expense_ref, transfer_fee
      const requiredHeaders = ['date', 'type', 'amount'];
      const hasRequired = requiredHeaders.every(h => headers.includes(h));
      
      if (!hasRequired) {
        toast.error(`CSV must contain: ${requiredHeaders.join(', ')}`);
        return;
      }

      let imported = 0;
      let failed = 0;
      const errors = [];

      // Process each line
      for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',').map(v => v.trim());
        
        if (values.length !== headers.length) {
          errors.push(`Row ${i + 1}: Column count mismatch`);
          failed++;
          continue;
        }

        const row = {};
        headers.forEach((header, idx) => {
          row[header] = values[idx];
        });

        try {
          const txType = row.type?.toLowerCase();
          
          // Find accounts by name
          const account = accounts.find(a => 
            a.name.toLowerCase() === row.account?.toLowerCase()
          );
          
          const fromAccount = accounts.find(a => 
            a.name.toLowerCase() === row.from_account?.toLowerCase()
          );
          
          const toAccount = accounts.find(a => 
            a.name.toLowerCase() === row.to_account?.toLowerCase()
          );

          // Find category by name
          const category = categories.find(c => 
            c.name.toLowerCase() === row.category?.toLowerCase()
          );

          // Build payload based on transaction type
          let payload = {
            type: txType,
            amount: parseFloat(row.amount),
            description: row.description || null,
            date: row.date ? new Date(row.date).toISOString() : new Date().toISOString(),
          };

          // Type-specific validation and payload construction
          if (txType === 'transfer') {
            if (!fromAccount || !toAccount) {
              errors.push(`Row ${i + 1}: Transfer needs valid from_account and to_account`);
              failed++;
              continue;
            }
            payload.from_account_uid = fromAccount.uid;
            payload.to_account_uid = toAccount.uid;
            payload.transfer_fee = row.transfer_fee ? parseFloat(row.transfer_fee) : null;
            
          } else if (txType === 'reimburse') {
            if (!account) {
              errors.push(`Row ${i + 1}: Reimburse needs valid account`);
              failed++;
              continue;
            }
            payload.account_uid = account.uid;
            
            // Handle expense reference - can be UID or description to look up
            if (row.expense_ref) {
              // Try to find the expense transaction by UID or description
              const expenseTx = transactions.find(tx => 
                tx.uid === row.expense_ref || 
                (tx.type === 'expense' && tx.description?.toLowerCase() === row.expense_ref.toLowerCase())
              );
              
              if (expenseTx) {
                payload.expense_uid = expenseTx.uid;
                // Inherit category from original expense if not specified
                if (!category && expenseTx.category_uid) {
                  payload.category_uid = expenseTx.category_uid;
                }
              } else {
                errors.push(`Row ${i + 1}: Could not find expense '${row.expense_ref}'`);
                failed++;
                continue;
              }
            } else {
              errors.push(`Row ${i + 1}: Reimburse needs expense_ref`);
              failed++;
              continue;
            }
            
          } else if (txType === 'income' || txType === 'expense') {
            if (!account) {
              errors.push(`Row ${i + 1}: ${txType} needs valid account`);
              failed++;
              continue;
            }
            if (!category) {
              errors.push(`Row ${i + 1}: ${txType} needs valid category`);
              failed++;
              continue;
            }
            payload.account_uid = account.uid;
            payload.category_uid = category.uid;
            
          } else {
            errors.push(`Row ${i + 1}: Invalid type '${txType}'`);
            failed++;
            continue;
          }

          await api.post("/transactions/", payload);
          imported++;
        } catch (err) {
          console.error(`Failed to import row ${i}:`, err);
          errors.push(`Row ${i + 1}: ${err.response?.data?.detail || err.message}`);
          failed++;
        }
      }

      // Show detailed results
      if (imported > 0) {
        toast.success(`✅ Imported ${imported} transactions successfully!`);
      }
      
      if (failed > 0) {
        const errorMsg = errors.slice(0, 5).join('\n');
        const moreErrors = errors.length > 5 ? `\n... and ${errors.length - 5} more errors` : '';
        toast.error(`❌ Failed ${failed} transactions:\n${errorMsg}${moreErrors}`, {
          duration: 8000,
        });
      }

      fetchData();
      setShowImport(false);
      e.target.value = ''; // Reset file input
    } catch (err) {
      console.error("Error importing CSV:", err);
      toast.error("Failed to import CSV");
    }
  };

  // Apply filters
  const filteredTransactions = transactions.filter(tx => {
    if (filters.type !== "all" && tx.type !== filters.type) return false;
    
    if (filters.accountUid !== "all") {
      const matchAccount = tx.account_uid === filters.accountUid ||
        tx.from_account_uid === filters.accountUid ||
        tx.to_account_uid === filters.accountUid;
      if (!matchAccount) return false;
    }
    
    if (filters.categoryUid !== "all" && tx.category_uid !== filters.categoryUid) return false;
    
    const txDate = new Date(tx.date);
    if (filters.dateFrom && txDate < new Date(filters.dateFrom)) return false;
    if (filters.dateTo && txDate > new Date(filters.dateTo)) return false;
    
    if (filters.minAmount && tx.amount < parseFloat(filters.minAmount)) return false;
    if (filters.maxAmount && tx.amount > parseFloat(filters.maxAmount)) return false;
    
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

  // Calculate summary
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
            onClick={() => setShowImport(!showImport)}
            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors shadow-md"
          >
            📥 Import CSV
          </button>
          <button
            onClick={() => setShowForm(true)}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors shadow-md"
          >
            + Add Transaction
          </button>
        </div>
      </div>

      {/* CSV Import Section */}
      {showImport && (
        <div className="bg-white rounded-lg shadow-md border p-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-lg font-semibold mb-2">📥 Import Transactions from CSV</h3>
              <p className="text-sm text-gray-600 mb-4">
                CSV format: date, type, amount, description, account, category, from_account, to_account, expense_ref, transfer_fee
              </p>
              <div className="text-xs text-gray-500 space-y-1">
                <p><strong>All Types:</strong></p>
                <p>• <strong>date</strong>: YYYY-MM-DD or MM/DD/YYYY (required)</p>
                <p>• <strong>type</strong>: income, expense, transfer, or reimburse (required)</p>
                <p>• <strong>amount</strong>: numeric value (required)</p>
                <p>• <strong>description</strong>: text description (optional)</p>
                <p className="mt-2"><strong>For Income/Expense:</strong></p>
                <p>• <strong>account</strong>: exact account name (required)</p>
                <p>• <strong>category</strong>: exact category name (required)</p>
                <p className="mt-2"><strong>For Transfer:</strong></p>
                <p>• <strong>from_account</strong>: source account name (required)</p>
                <p>• <strong>to_account</strong>: destination account name (required)</p>
                <p>• <strong>transfer_fee</strong>: fee amount if any (optional)</p>
                <p className="mt-2"><strong>For Reimburse:</strong></p>
                <p>• <strong>account</strong>: reimbursement destination account (required)</p>
                <p>• <strong>expense_ref</strong>: original expense UID or description (required)</p>
              </div>
            </div>
            <button
              onClick={() => setShowImport(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select CSV File
            </label>
            <input
              type="file"
              accept=".csv"
              onChange={handleImportCSV}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm font-medium mb-2">Example CSV:</p>
            <pre className="text-xs bg-white p-3 rounded border overflow-x-auto">
date,type,amount,description,account,category,from_account,to_account,expense_ref,transfer_fee
2024-01-15,expense,50.00,Groceries,Cash,Food,,,,
2024-01-16,income,2000.00,Salary,Bank,Income,,,,
2024-01-17,transfer,500.00,Savings transfer,,,Checking,Savings,,10.00
2024-01-18,reimburse,50.00,Groceries refund,Cash,,,,,
            </pre>
            <div className="mt-3 text-xs text-gray-600 space-y-1">
              <p><strong>Transfers:</strong> Use from_account and to_account columns (leave account/category blank)</p>
              <p><strong>Reimburse:</strong> Use expense_ref to reference original expense by UID or description</p>
              <p><strong>Income/Expense:</strong> Use account and category columns (standard format)</p>
            </div>
          </div>
        </div>
      )}

      {/* Transaction Form Modal */}
      {showForm && (
        <TransactionForm
          onClose={() => setShowForm(false)}
          onSuccess={() => {
            fetchData();
            setShowForm(false);
          }}
        />
      )}

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
          <div className="md:col-span-2">
            <input
              type="text"
              placeholder="🔍 Search description, account, category..."
              value={filters.searchTerm}
              onChange={(e) => setFilters({...filters, searchTerm: e.target.value})}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            />
          </div>
          
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
          
          <input
            type="date"
            value={filters.dateFrom}
            onChange={(e) => setFilters({...filters, dateFrom: e.target.value})}
            className="border rounded-lg px-3 py-2 text-sm"
            placeholder="From date"
          />
          
          <input
            type="date"
            value={filters.dateTo}
            onChange={(e) => setFilters({...filters, dateTo: e.target.value})}
            className="border rounded-lg px-3 py-2 text-sm"
            placeholder="To date"
          />
          
          <input
            type="number"
            placeholder="Min amount"
            value={filters.minAmount}
            onChange={(e) => setFilters({...filters, minAmount: e.target.value})}
            className="border rounded-lg px-3 py-2 text-sm"
          />
          
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
                  <th className="px-4 py-3 text-left font-semibold">Description</th>
                  <th className="px-4 py-3 text-center font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody>
                {sortedTransactions.map((tx) => (
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
          {sortedTransactions.map((tx) => (
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
            </div>
          ))}
        </div>
      )}
    </div>
  );
}