// frontend/src/components/dashboard/CategoryBudgets.jsx

import React from "react";

export default function CategoryBudgets({ categories }) {
  const usage = categories.budget > 0 ? categories.budget_used / categories.budget : 0;
  const pct = Math.min(usage * 100, 100).toFixed(1);
  const color =
    usage > 1 ? "bg-red-500" : usage > 0.7 ? "bg-yellow-400" : "bg-green-500";

  return (
    <div>
      <div className="flex justify-between">
        <span>{categories.name}</span>
        <span className="text-sm text-gray-500">
          ₱{categories.budget_used?.toLocaleString() || 0} / ₱
          {categories.budget?.toLocaleString() || 0} ({pct}%)
        </span>
      </div>
      <div className="h-2 bg-gray-200 rounded mt-1">
        <div className={`h-2 ${color} rounded`} style={{ width: `${pct}%` }}></div>
      </div>

      {categories.children?.length > 0 && (
        <div className="ml-4 mt-2 space-y-1">
          {categories.children.map((child) => (
            <categoriesBudget key={child.uid} categories={child} />
          ))}
        </div>
      )}
    </div>
  );
}