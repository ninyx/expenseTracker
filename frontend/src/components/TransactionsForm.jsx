import { useEffect, useState } from "react";
import { createTransaction } from "../services/transactions";
import api from "../services/api";
import toast from "react-hot-toast";

export default function TransactionForm({ onClose, onSuccess }) {
  const [form, setForm] = useState({
    type: "expense",
    amount: "",
    description: "",
    account_uid: "",
    category_uid: "",
    from_account_uid: "",
    to_account_uid: "",
    expense_uid: "",
    transfer_fee: "",
    date: new Date().toISOString().slice(0, 16), // prefill current datetime
  });

  const [accounts, setAccounts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Fetch dropdown data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [accRes, catRes, txRes] = await Promise.all([
          api.get("/accounts/"),
          api.get("/categories/"),
          api.get("/transactions/"),
        ]);
        setAccounts(accRes.data);
        setCategories(catRes.data);
        setTransactions(txRes.data);
      } catch (err) {
        console.error("Error fetching dropdown data:", err);
        toast.error("Failed to load dropdown data.");
      }
    };
    fetchData();
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const payload = {
      type: form.type,
      amount: parseFloat(form.amount),
      description: form.description || null,
      account_uid: form.account_uid || null,
      category_uid: form.category_uid || null,
      from_account_uid: form.from_account_uid || null,
      to_account_uid: form.to_account_uid || null,
      expense_uid: form.expense_uid || null,
      transfer_fee:
        form.transfer_fee !== "" ? parseFloat(form.transfer_fee) : null,
      date: new Date(form.date).toISOString(),
    };

    try {
      await createTransaction(payload);
      toast.success("Transaction created successfully!");
      onSuccess();
      onClose();
    } catch (err) {
      console.error(err);
      toast.error(
        err.response?.data?.detail || "Failed to create transaction."
      );
      setError("Transaction creation failed.");
    } finally {
      setLoading(false);
    }
  };

  const expenseOptions = transactions.filter((tx) => tx.type === "expense");

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/50 z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-lg relative overflow-y-auto max-h-[90vh]">
        <h2 className="text-xl font-semibold mb-4">Add Transaction</h2>

        <form onSubmit={handleSubmit} className="space-y-3">
          {/* Type */}
          <div>
            <label className="block text-sm mb-1">Type</label>
            <select
              name="type"
              value={form.type}
              onChange={handleChange}
              className="border p-2 rounded w-full"
              required
            >
              <option value="income">Income</option>
              <option value="expense">Expense</option>
              <option value="transfer">Transfer</option>
              <option value="reimburse">Reimburse</option>
            </select>
          </div>

          {/* Amount */}
          <div>
            <label className="block text-sm mb-1">Amount</label>
            <input
              type="number"
              name="amount"
              step="0.01"
              value={form.amount}
              onChange={handleChange}
              className="border p-2 rounded w-full"
              required
            />
          </div>

          {/* Date */}
          <div>
            <label className="block text-sm mb-1">Date</label>
            <input
              type="datetime-local"
              name="date"
              value={form.date}
              onChange={handleChange}
              className="border p-2 rounded w-full"
              required
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm mb-1">Description</label>
            <input
              type="text"
              name="description"
              value={form.description}
              onChange={handleChange}
              className="border p-2 rounded w-full"
              placeholder="Optional"
            />
          </div>

          {/* Account */}
          {(form.type === "income" || form.type === "expense" || form.type === "reimburse") && (
            <div>
              <label className="block text-sm mb-1">Account</label>
              <select
                name="account_uid"
                value={form.account_uid}
                onChange={handleChange}
                className="border p-2 rounded w-full"
                required
              >
                <option value="">Select account</option>
                {accounts.map((acc) => (
                  <option key={acc.uid} value={acc.uid}>
                    {acc.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Category */}
          {(form.type === "income" || form.type === "expense") && (
            <div>
              <label className="block text-sm mb-1">Category</label>
              <select
                name="category_uid"
                value={form.category_uid}
                onChange={handleChange}
                className="border p-2 rounded w-full"
                required
              >
                <option value="">Select category</option>
                {categories.map((cat) => (
                  <option key={cat.uid} value={cat.uid}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Transfer Fields */}
          {form.type === "transfer" && (
            <>
              <div>
                <label className="block text-sm mb-1">From Account</label>
                <select
                  name="from_account_uid"
                  value={form.from_account_uid}
                  onChange={handleChange}
                  className="border p-2 rounded w-full"
                  required
                >
                  <option value="">Select source account</option>
                  {accounts.map((acc) => (
                    <option key={acc.uid} value={acc.uid}>
                      {acc.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm mb-1">To Account</label>
                <select
                  name="to_account_uid"
                  value={form.to_account_uid}
                  onChange={handleChange}
                  className="border p-2 rounded w-full"
                  required
                >
                  <option value="">Select destination account</option>
                  {accounts.map((acc) => (
                    <option key={acc.uid} value={acc.uid}>
                      {acc.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm mb-1">Transfer Fee (optional)</label>
                <input
                  type="number"
                  name="transfer_fee"
                  step="0.01"
                  value={form.transfer_fee}
                  onChange={handleChange}
                  className="border p-2 rounded w-full"
                  placeholder="₱0.00"
                />
              </div>
            </>
          )}

          {/* Reimburse */}
          {form.type === "reimburse" && (
            <div>
              <label className="block text-sm mb-1">Reimbursed Expense</label>
              <select
                name="expense_uid"
                value={form.expense_uid}
                onChange={handleChange}
                className="border p-2 rounded w-full"
                required
              >
                <option value="">Select expense to reimburse</option>
                {expenseOptions.map((tx) => (
                  <option key={tx.uid} value={tx.uid}>
                    {tx.description
                      ? `${tx.description} — ₱${tx.amount}`
                      : `Expense ₱${tx.amount}`}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Buttons */}
          <div className="flex justify-end gap-2 mt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded bg-gray-200 hover:bg-gray-300"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700"
            >
              {loading ? "Saving..." : "Save"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
