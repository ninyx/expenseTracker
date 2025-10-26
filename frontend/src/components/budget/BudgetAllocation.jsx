// frontend/src/components/budget/BudgetAllocation.jsx
import { useState } from "react";
import { updateCategory } from "../../services/categories";
import toast from "react-hot-toast";

export default function BudgetAllocation({ categories, onUpdate }) {
  const [editingId, setEditingId] = useState(null);
  const [editValues, setEditValues] = useState({ budget: "", frequency: "" });

  const startEdit = (cat) => {
    setEditingId(cat.uid);
    setEditValues({
      budget: cat.budget || "",
      frequency: cat.frequency || "monthly",
    });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditValues({ budget: "", frequency: "" });
  };

  const saveEdit = async (uid) => {
    try {
      await updateCategory(uid, {
        budget: parseFloat(editValues.budget) || 0,
        frequency: editValues.frequency,
      });
      toast.success("Budget updated successfully!");
      onUpdate();
      cancelEdit();
    } catch (err) {
      console.error(err);
      toast.error("Failed to update budget");
    }
  };

  const renderCategory = (cat, depth = 0) => {
    const isEditing = editingId === cat.uid;
    const percentage = cat.budget > 0 ? ((cat.budget_used || 0) / cat.budget) * 100 : 0;
    const statusColor =
      percentage >= 100 ? "text-red-600" : percentage >= 80 ? "text-yellow-600" : "text-green-600";

    return (
      <div key={cat.uid}>
        <div
          className={`grid grid-cols-7 gap-4 p-3 border-b hover:bg-gray-50 items-center ${
            depth > 0 ? "bg-gray-50" : ""
          }`}
          style={{ paddingLeft: `${depth * 2 + 1}rem` }}
        >
          {/* Category Name */}
          <div className="col-span-2 font-medium flex items-center gap-2">
            {depth > 0 && <span className="text-gray-400">└─</span>}
            <span className="truncate">{cat.name}</span>
          </div>

          {/* Budget */}
          <div>
            {isEditing ? (
              <input
                type="number"
                step="0.01"
                value={editValues.budget}
                onChange={(e) =>
                  setEditValues({ ...editValues, budget: e.target.value })
                }
                className="border rounded px-2 py-1 w-full text-sm"
                placeholder="0.00"
              />
            ) : (
              <span className="text-sm">₱{(cat.budget || 0).toLocaleString()}</span>
            )}
          </div>

          {/* Used */}
          <div className={`${statusColor} font-medium text-sm`}>
            ₱{(cat.budget_used || 0).toLocaleString()}
          </div>

          {/* Remaining */}
          <div className={`font-medium text-sm ${cat.budget - (cat.budget_used || 0) < 0 ? "text-red-600" : "text-green-600"}`}>
            ₱{(cat.budget - (cat.budget_used || 0)).toLocaleString()}
          </div>

          {/* Frequency */}
          <div>
            {isEditing ? (
              <select
                value={editValues.frequency}
                onChange={(e) =>
                  setEditValues({ ...editValues, frequency: e.target.value })
                }
                className="border rounded px-2 py-1 w-full text-sm"
              >
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
                <option value="one-time">One-time</option>
              </select>
            ) : (
              <span className="text-xs capitalize text-gray-600">{cat.frequency || "—"}</span>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-2 justify-end">
            {isEditing ? (
              <>
                <button
                  onClick={() => saveEdit(cat.uid)}
                  className="text-green-600 hover:underline text-sm font-medium"
                >
                  ✓ Save
                </button>
                <button
                  onClick={cancelEdit}
                  className="text-gray-600 hover:underline text-sm"
                >
                  ✕ Cancel
                </button>
              </>
            ) : (
              <button
                onClick={() => startEdit(cat)}
                className="text-blue-600 hover:underline text-sm font-medium"
              >
                ✏️ Edit
              </button>
            )}
          </div>
        </div>

        {/* Render Children */}
        {cat.children &&
          cat.children.map((child) => renderCategory(child, depth + 1))}
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md border overflow-hidden">
      <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-b">
        <h3 className="text-lg font-semibold text-gray-800">📋 Budget Allocation Table</h3>
        <p className="text-sm text-gray-600 mt-1">Manage and track your budget allocations</p>
      </div>

      <div className="overflow-x-auto">
        {/* Table Header */}
        <div className="grid grid-cols-7 gap-4 p-3 bg-gray-100 font-semibold text-sm border-b text-gray-700">
          <div className="col-span-2">Category</div>
          <div>Budget</div>
          <div>Used</div>
          <div>Remaining</div>
          <div>Frequency</div>
          <div className="text-right">Actions</div>
        </div>

        {/* Table Body */}
        {categories.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <div className="text-4xl mb-2">📊</div>
            <p className="font-medium">No budget allocations found</p>
            <p className="text-sm mt-1">No categories match this frequency period.</p>
          </div>
        ) : (
          <div className="divide-y">
            {categories.map((cat) => renderCategory(cat))}
          </div>
        )}
      </div>
    </div>
  );
}