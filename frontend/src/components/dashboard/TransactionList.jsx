
// src/components/dashboard/TransactionsList.jsx
import React, { useState } from "react";

// Single transaction component
function TransactionItem({ tx, accounts = [], categories = [] }) {
  if (!tx) return null; // defensive

  const [expanded, setExpanded] = useState(false);

  const account = accounts.find((a) => a.uid === tx.account_uid);
  const category = categories.find((c) => c.uid === tx.category_uid);

  const typeColors = {
    income: { bg: "bg-green-100", text: "text-green-700", amount: "text-green-600", icon: "💰" },
    expense: { bg: "bg-red-100", text: "text-red-700", amount: "text-red-600", icon: "🛒" },
    reimburse: { bg: "bg-amber-100", text: "text-amber-700", amount: "text-amber-600", icon: "💵" },
    transfer: { bg: "bg-blue-100", text: "text-blue-700", amount: "text-blue-600", icon: "🔁" },
  };

  const txType = tx.transaction_type || tx.type || "other";
  const colors = typeColors[txType] || { bg: "bg-gray-100", text: "text-gray-700", amount: "text-gray-600", icon: "💼" };

  return (
    <div
      className="border-b py-3 last:border-none cursor-pointer hover:bg-gray-50 transition-colors rounded-sm"
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex justify-between items-center">
        <div className="flex flex-col">
          <p className="font-medium flex items-center gap-1">
            <span>{colors.icon}</span> {tx.description || tx.name || "No description"}
          </p>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span>{tx.date ? new Date(tx.date).toLocaleDateString() : "No date"}</span>
            <span className={`font-semibold px-2 py-0.5 rounded-full ${colors.bg} ${colors.text}`}>
              {txType}
            </span>
          </div>
        </div>
        <p className={`font-semibold ${colors.amount}`}>
          ₱{Number(tx.amount || 0).toLocaleString()}
        </p>
      </div>

      {expanded && (
        <div className="text-xs text-gray-700 mt-2 ml-2 space-y-1 border-l-2 border-gray-200 pl-3">
          {account && <p>💳 <span className="font-medium">{account.name}</span></p>}
          {category && <p>🗂 <span className="font-medium">{category.name}</span></p>}
          {tx.transfer_fee > 0 && <p>💸 Transfer Fee: ₱{Number(tx.transfer_fee).toLocaleString()}</p>}
          {tx.notes && <p>📝 {tx.notes}</p>}
        </div>
      )}
    </div>
  );
}

// Wrapper for the transactions list
export default function TransactionsList({ transactions = [], accounts = [], categories = [] }) {
  return (
    <div className="space-y-2">
      {transactions
        .filter(Boolean) // remove undefined/null
        .map((tx) => (
          <TransactionItem key={tx.uid || tx.id || Math.random()} tx={tx} accounts={accounts} categories={categories} />
        ))}
    </div>
  );
}
