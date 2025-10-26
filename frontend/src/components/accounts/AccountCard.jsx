// frontend/src/components/accounts/AccountCard.jsx
import { useState } from "react";

export default function AccountCard({ account, onDelete, onUpdate }) {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    name: account.name,
    type: account.type,
    interest_rate: account.interest_rate || 0,
    interest_frequency: account.interest_frequency || "monthly",
  });

  const handleSave = () => {
    onUpdate(account.uid, editData);
    setIsEditing(false);
  };

  const getAccountIcon = (type) => {
    const icons = {
      cash: "💵",
      checking: "🏦",
      savings: "💰",
      "credit card": "💳",
      loan: "📋",
      mortgage: "🏠",
      investment: "📈",
      retirement: "🎯",
      "digital wallet": "📱",
    };
    return icons[type] || "💼";
  };

  const getTypeColor = (type) => {
    const colors = {
      cash: "bg-green-100 text-green-700 border-green-200",
      checking: "bg-blue-100 text-blue-700 border-blue-200",
      savings: "bg-purple-100 text-purple-700 border-purple-200",
      "credit card": "bg-orange-100 text-orange-700 border-orange-200",
      loan: "bg-red-100 text-red-700 border-red-200",
      mortgage: "bg-pink-100 text-pink-700 border-pink-200",
      investment: "bg-indigo-100 text-indigo-700 border-indigo-200",
      retirement: "bg-teal-100 text-teal-700 border-teal-200",
      "digital wallet": "bg-cyan-100 text-cyan-700 border-cyan-200",
    };
    return colors[type] || "bg-gray-100 text-gray-700 border-gray-200";
  };

  // Calculate projected interest (monthly)
  const monthlyInterest = account.interest_rate
    ? (account.balance * (account.interest_rate / 100)) / 12
    : 0;

  return (
    <div className="bg-white rounded-xl shadow-lg border hover:shadow-xl transition-shadow overflow-hidden">
      {/* Card Header */}
      <div className={`p-4 ${getTypeColor(account.type)} border-b`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-3xl">{getAccountIcon(account.type)}</span>
            <div>
              {isEditing ? (
                <input
                  type="text"
                  value={editData.name}
                  onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                  className="font-semibold text-lg px-2 py-1 border rounded"
                />
              ) : (
                <h3 className="font-semibold text-lg">{account.name}</h3>
              )}
              <p className="text-sm capitalize opacity-80">{account.type}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Card Body */}
      <div className="p-6 space-y-4">
        {/* Balance */}
        <div>
          <p className="text-sm text-gray-600 mb-1">Current Balance</p>
          <p className="text-3xl font-bold text-gray-800">
            ₱{account.balance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>

        {/* Interest Information */}
        {account.interest_rate > 0 && (
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 border border-green-200">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Interest Rate</span>
              {isEditing ? (
                <input
                  type="number"
                  step="0.01"
                  value={editData.interest_rate}
                  onChange={(e) => setEditData({ ...editData, interest_rate: e.target.value })}
                  className="text-lg font-bold text-green-700 px-2 py-1 border rounded w-24"
                />
              ) : (
                <span className="text-lg font-bold text-green-700">
                  {account.interest_rate}% APR
                </span>
              )}
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Monthly Interest</span>
              <span className="font-semibold text-green-600">
                ≈ ₱{monthlyInterest.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            </div>
            {isEditing && (
              <div className="mt-2">
                <select
                  value={editData.interest_frequency}
                  onChange={(e) => setEditData({ ...editData, interest_frequency: e.target.value })}
                  className="text-sm px-2 py-1 border rounded w-full"
                >
                  <option value="monthly">Monthly</option>
                  <option value="quarterly">Quarterly</option>
                  <option value="annually">Annually</option>
                </select>
              </div>
            )}
          </div>
        )}

        {/* Description */}
        {account.description && (
          <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
            {account.description}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2 pt-4 border-t">
          {isEditing ? (
            <>
              <button
                onClick={handleSave}
                className="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition-colors font-medium"
              >
                ✓ Save
              </button>
              <button
                onClick={() => setIsEditing(false)}
                className="flex-1 bg-gray-200 text-gray-700 py-2 rounded-lg hover:bg-gray-300 transition-colors"
              >
                ✕ Cancel
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => setIsEditing(true)}
                className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                ✏️ Edit
              </button>
              <button
                onClick={() => onDelete(account.uid)}
                className="flex-1 bg-red-600 text-white py-2 rounded-lg hover:bg-red-700 transition-colors font-medium"
              >
                🗑️ Delete
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}