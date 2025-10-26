// frontend/src/components/accounts/AccountForm.jsx
import { useState } from "react";

export default function AccountForm({ onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    name: "",
    type: "",
    balance: "",
    interest_rate: "",
    interest_frequency: "monthly",
    description: "",
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name || !formData.type) return;

    onSubmit({
      name: formData.name,
      type: formData.type,
      balance: parseFloat(formData.balance) || 0,
      interest_rate: parseFloat(formData.interest_rate) || 0,
      interest_frequency: formData.interest_frequency,
      description: formData.description,
    });

    // Reset form
    setFormData({
      name: "",
      type: "",
      balance: "",
      interest_rate: "",
      interest_frequency: "monthly",
      description: "",
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Account Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Account Name *
          </label>
          <input
            type="text"
            className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g., BPI Savings"
            required
          />
        </div>

        {/* Account Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Account Type *
          </label>
          <select
            className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            value={formData.type}
            onChange={(e) => setFormData({ ...formData, type: e.target.value })}
            required
          >
            <option value="">Select type</option>
            <option value="cash">💵 Cash</option>
            <option value="checking">🏦 Checking</option>
            <option value="savings">💰 Savings</option>
            <option value="credit card">💳 Credit Card</option>
            <option value="loan">📋 Loan</option>
            <option value="mortgage">🏠 Mortgage</option>
            <option value="investment">📈 Investment</option>
            <option value="retirement">🎯 Retirement</option>
            <option value="digital wallet">📱 Digital Wallet</option>
          </select>
        </div>

        {/* Initial Balance */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Initial Balance
          </label>
          <input
            type="number"
            step="0.01"
            className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            value={formData.balance}
            onChange={(e) => setFormData({ ...formData, balance: e.target.value })}
            placeholder="₱0.00"
          />
        </div>

        {/* Interest Rate */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Interest Rate (% APR)
          </label>
          <input
            type="number"
            step="0.01"
            className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            value={formData.interest_rate}
            onChange={(e) => setFormData({ ...formData, interest_rate: e.target.value })}
            placeholder="e.g., 2.5"
          />
          <p className="text-xs text-gray-500 mt-1">
            Annual Percentage Rate (leave blank if no interest)
          </p>
        </div>

        {/* Interest Frequency */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Interest Frequency
          </label>
          <select
            className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            value={formData.interest_frequency}
            onChange={(e) => setFormData({ ...formData, interest_frequency: e.target.value })}
          >
            <option value="monthly">Monthly</option>
            <option value="quarterly">Quarterly</option>
            <option value="annually">Annually</option>
          </select>
        </div>

        {/* Description */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description (Optional)
          </label>
          <textarea
            className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Add notes about this account..."
            rows="3"
          />
        </div>
      </div>

      {/* Form Actions */}
      <div className="flex justify-end gap-3 pt-4 border-t">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-6 py-2 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Create Account
        </button>
      </div>
    </form>
  );
}