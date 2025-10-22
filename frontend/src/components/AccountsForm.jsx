import { useState } from "react";

export default function AccountForm({ onSubmit }) {
  const [name, setName] = useState("");
  const [type, setType] = useState("");
  const [balance, setBalance] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name || !type) return;
    onSubmit({ name, type, balance: parseFloat(balance) || 0 });
    setName("");
    setType("");
    setBalance("");
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3 bg-gray-50 p-4 rounded-lg shadow-inner">
      <div>
        <label className="block text-sm font-medium">Account Name</label>
        <input
          className="border rounded-md p-2 w-full"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g. BPI Savings"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium">Type</label>
        <select
          className="border rounded-md p-2 w-full"
          value={type}
          onChange={(e) => setType(e.target.value)}
          required
        >

          <option value="">Select type</option>
            <option value="cash">cash</option>
            <option value="checking">checking</option>
            <option value="savings">savings</option>
            <option value="credit card">credit card</option>
            <option value="loan">loan</option>
            <option value="mortgage">mortgage</option>
            <option value="investment">investment</option>
            <option value="retirement">retirement</option>
            <option value="digital wallet">digital wallet</option>
            
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium">Initial Balance</label>
        <input
          type="number"
          className="border rounded-md p-2 w-full"
          value={balance}
          onChange={(e) => setBalance(e.target.value)}
          placeholder="₱0.00"
        />
      </div>

      <button
        type="submit"
        className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
      >
        Add Account
      </button>
    </form>
  );
}
