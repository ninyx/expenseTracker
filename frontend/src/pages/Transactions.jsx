import { useEffect, useState } from "react";
import {
  getTransactions,
  deleteTransaction,
} from "../services/transactions";
import TransactionForm from "../components/TransactionsForm.jsx";

export default function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);

  const fetchTransactions = async () => {
    try {
      const data = await getTransactions();
      setTransactions(data);
    } catch (err) {
      console.error("Error fetching transactions:", err);
      setError("Failed to load transactions.");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (uid) => {
    if (!confirm("Delete this transaction?")) return;
    try {
      await deleteTransaction(uid);
      setTransactions((prev) => prev.filter((tx) => tx.uid !== uid));
    } catch (err) {
      alert("Failed to delete transaction.");
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, []);

  if (loading) return <p className="text-center p-6">Loading transactions...</p>;
  if (error) return <p className="text-red-500 p-6">{error}</p>;

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold">Transactions</h1>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          + Add Transaction
        </button>
      </div>

      {transactions.length === 0 ? (
        <p>No transactions found.</p>
      ) : (
        <table className="w-full border-collapse border border-gray-300 text-sm">
          <thead className="bg-gray-100">
            <tr>
              <th className="border px-3 py-2 text-left">Date</th>
              <th className="border px-3 py-2 text-left">Type</th>
              <th className="border px-3 py-2 text-left">Account</th>
              <th className="border px-3 py-2 text-left">Category</th>
              <th className="border px-3 py-2 text-left">Amount</th>
              <th className="border px-3 py-2 text-left">Description</th>
              <th className="border px-3 py-2 text-left">Details</th>
              <th className="border px-3 py-2 text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((tx) => (
              <tr key={tx.uid} className="hover:bg-gray-50">
                <td className="border px-3 py-2">
                  {new Date(tx.date).toLocaleDateString()}
                </td>
                <td className="border px-3 py-2 capitalize">{tx.type}</td>
                <td className="border px-3 py-2">
                  {tx.account_name ||
                    tx.from_account_name ||
                    "—"}
                </td>
                <td className="border px-3 py-2">
                  {tx.category_name ||
                    tx.to_account_name ||
                    "—"}
                </td>
                <td
                  className={`border px-3 py-2 font-semibold ${
                    tx.type === "expense"
                      ? "text-red-500"
                      : tx.type === "income"
                      ? "text-green-600"
                      : "text-blue-500"
                  }`}
                >
                  ₱{tx.amount.toLocaleString()}
                </td>
                <td className="border px-3 py-2">{tx.description || "—"}</td>
                <td className="border px-3 py-2">
                  {tx.type === "transfer" && (
                    <span>
                      {tx.from_account_name} → {tx.to_account_name}
                    </span>
                  )}
                  {tx.type === "reimburse" && tx.reimbursed_transaction && (
                    <span className="italic text-gray-600">
                      Reimbursed: {tx.reimbursed_transaction.description}
                    </span>
                  )}
                </td>
                <td className="border px-3 py-2 text-center">
                  <button
                    onClick={() => handleDelete(tx.uid)}
                    className="text-red-600 hover:underline"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {showForm && (
        <TransactionForm
          onClose={() => setShowForm(false)}
          onSuccess={fetchTransactions}
        />
      )}
    </div>
  );
}
