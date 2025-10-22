import { useEffect, useState } from "react";
import {
  getAccounts,
  createAccount,
  deleteAccount,
  updateAccount,
} from "../services/accounts";

import AccountList from "../components/AccountsList.jsx";
import AccountForm from "../components/AccountsForm.jsx";

export default function Accounts() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchAccounts = async () => {
    try {
      const data = await getAccounts();
      setAccounts(data);
    } catch (err) {
      console.error("Error fetching accounts:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddAccount = async (accountData) => {
    try {
      const newAcc = await createAccount(accountData);
      setAccounts((prev) => [...prev, newAcc]);
    } catch (err) {
      console.error("Error creating account:", err);
    }
  };

  const handleDeleteAccount = async (uid) => {
    if (!confirm("Are you sure you want to delete this account?")) return;
    try {
      await deleteAccount(uid);
      setAccounts((prev) => prev.filter((acc) => acc.uid !== uid));
    } catch (err) {
      console.error("Error deleting account:", err);
    }
  };

  const handleUpdateAccount = async (uid, newData) => {
    try {
      const updated = await updateAccount(uid, newData);
      setAccounts((prev) =>
        prev.map((acc) => (acc.uid === uid ? updated : acc))
      );
    } catch (err) {
      console.error("Error updating account:", err);
    }
  };

  useEffect(() => {
    fetchAccounts();
  }, []);

  if (loading) return <p>Loading...</p>;

  return (
    <div className="space-y-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-semibold">Accounts</h1>
      <AccountForm onSubmit={handleAddAccount} />
      <AccountList
        accounts={accounts}
        onDelete={handleDeleteAccount}
        onUpdate={handleUpdateAccount}
      />
    </div>
  );
}
