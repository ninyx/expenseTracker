// frontend/src/pages/Accounts.jsx - Enhanced Version
import { useEffect, useState } from "react";
import {
  getAccounts,
  createAccount,
  deleteAccount,
  updateAccount,
} from "../services/accounts";
import toast from "react-hot-toast";
import AccountCard from "../components/accounts/AccountCard.jsx";
import AccountSummary from "../components/accounts/AccountSummary.jsx";
import AccountForm from "../components/accounts/AccountForm.jsx";

export default function Accounts() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  const fetchAccounts = async () => {
    try {
      const data = await getAccounts();
      setAccounts(data);
    } catch (err) {
      console.error("Error fetching accounts:", err);
      toast.error("Failed to load accounts");
    } finally {
      setLoading(false);
    }
  };

  const handleAddAccount = async (accountData) => {
    try {
      const newAcc = await createAccount(accountData);
      setAccounts((prev) => [...prev, newAcc]);
      toast.success("Account created successfully!");
      setShowForm(false);
    } catch (err) {
      console.error("Error creating account:", err);
      toast.error("Failed to create account");
    }
  };

  const handleDeleteAccount = async (uid) => {
    if (!confirm("Are you sure you want to delete this account?")) return;
    try {
      await deleteAccount(uid);
      setAccounts((prev) => prev.filter((acc) => acc.uid !== uid));
      toast.success("Account deleted successfully!");
    } catch (err) {
      console.error("Error deleting account:", err);
      toast.error("Failed to delete account");
    }
  };

  const handleUpdateAccount = async (uid, newData) => {
    try {
      const updated = await updateAccount(uid, newData);
      setAccounts((prev) =>
        prev.map((acc) => (acc.uid === uid ? updated : acc))
      );
      toast.success("Account updated successfully!");
    } catch (err) {
      console.error("Error updating account:", err);
      toast.error("Failed to update account");
    }
  };

  useEffect(() => {
    fetchAccounts();
  }, []);

  if (loading) {
    return (
      <div className="p-6 text-center">
        <p className="text-gray-500">Loading accounts...</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">💳 Accounts</h1>
          <p className="text-gray-600 mt-1">Manage your financial accounts and track interest</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors shadow-md flex items-center gap-2"
        >
          {showForm ? "✕ Cancel" : "+ Add Account"}
        </button>
      </div>

      {/* Account Summary */}
      <AccountSummary accounts={accounts} />

      {/* Add Account Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow-lg border p-6">
          <h2 className="text-xl font-semibold mb-4">Create New Account</h2>
          <AccountForm onSubmit={handleAddAccount} onCancel={() => setShowForm(false)} />
        </div>
      )}

      {/* Accounts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {accounts.length === 0 ? (
          <div className="col-span-full bg-white rounded-lg p-12 text-center border shadow-sm">
            <div className="text-6xl mb-4">💳</div>
            <p className="text-lg font-medium text-gray-700 mb-2">No Accounts Yet</p>
            <p className="text-gray-500">Create your first account to get started</p>
            <button
              onClick={() => setShowForm(true)}
              className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
            >
              Add Your First Account
            </button>
          </div>
        ) : (
          accounts.map((acc) => (
            <AccountCard
              key={acc.uid}
              account={acc}
              onDelete={handleDeleteAccount}
              onUpdate={handleUpdateAccount}
            />
          ))
        )}
      </div>
    </div>
  );
}