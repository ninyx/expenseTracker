// src/components/dashboard/SummaryCards.jsx
import React from "react";

export default function SummaryCards({ totals }) {
  const cards = [
    { label: "Total Income", value: totals.income, color: "text-green-600" },
    { label: "Total Expense", value: totals.expense, color: "text-red-600" },
    { label: "Total Balance", value: totals.balance, color: "text-blue-600" },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {cards.map((card) => (
        <div key={card.label} className="bg-white p-4 rounded shadow-sm border">
          <p className="text-gray-500 text-sm">{card.label}</p>
          <p className={`text-xl font-bold ${card.color}`}>
            ₱{card.value.toLocaleString()}
          </p>
        </div>
      ))}
    </div>
  );
}
