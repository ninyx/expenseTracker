// src/components/CategoriesForm.jsx
import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";

export default function CategoriesForm({
  categories,
  onSubmit,
  editingCategory,
  onCancel,
}) {
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    transaction_type: "expense",
    parent_uid: "",
    budget: "",
    frequency: "monthly",
  });

  useEffect(() => {
    if (editingCategory) {
      setFormData({
        name: editingCategory.name || "",
        description: editingCategory.description || "",
        transaction_type: editingCategory.transaction_type || "expense",
        parent_uid: editingCategory.parent_uid || "",
        budget: editingCategory.budget || "",
        frequency: editingCategory.frequency || "monthly",
      });
    } else {
      setFormData({
        name: "",
        description: "",
        transaction_type: "expense",
        parent_uid: "",
        budget: "",
        frequency: "monthly",
      });
    }
  }, [editingCategory]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = {
      ...formData,
      budget: formData.budget
        ? parseFloat(formData.budget)
        : 0,
      parent_uid: formData.parent_uid || null,
    };

    try {
      await onSubmit(payload);
      setFormData({
        name: "",
        description: "",
        transaction_type: "expense",
        parent_uid: "",
        budget: "",
        frequency: "monthly",
      });
    } catch (err) {
      console.error(err);
      toast.error("Failed to save category");
    }
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-md border mb-6">
      <h2 className="text-lg font-semibold mb-3">
        {editingCategory ? "✏️ Edit Category" : "➕ Add Category"}
      </h2>

      <form
        onSubmit={handleSubmit}
        className="grid grid-cols-1 sm:grid-cols-2 gap-3"
      >
        <div>
          <label className="text-sm text-gray-600">Name</label>
          <input
            type="text"
            required
            value={formData.name}
            onChange={(e) =>
              setFormData({ ...formData, name: e.target.value })
            }
            className="border rounded p-2 w-full"
          />
        </div>

        <div>
          <label className="text-sm text-gray-600">Transaction Type</label>
          <select
            value={formData.transaction_type}
            onChange={(e) =>
              setFormData({ ...formData, transaction_type: e.target.value })
            }
            className="border rounded p-2 w-full"
          >
            <option value="expense">expense</option>
            <option value="income">income</option>
          </select>
        </div>

        <div>
          <label className="text-sm text-gray-600">Parent Category</label>
          <select
            value={formData.parent_uid}
            onChange={(e) =>
              setFormData({ ...formData, parent_uid: e.target.value })
            }
            className="border rounded p-2 w-full"
          >
            <option value="">— None —</option>
            {categories.flatMap(flattenCategories).map((c) => (
              <option key={c.uid} value={c.uid}>
                {c.indent + c.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-sm text-gray-600">Frequency</label>
          <select
            value={formData.frequency}
            onChange={(e) =>
              setFormData({ ...formData, frequency: e.target.value })
            }
            className="border rounded p-2 w-full"
          >
            <option value="monthly">monthly</option>
            <option value="weekly">weekly</option>
            <option value="yearly">yearly</option>
            <option value="one-time">one-time</option>
          </select>
        </div>

        <div>
          <label className="text-sm text-gray-600">Budget (₱)</label>
          <input
            type="number"
            step="0.01"
            value={formData.budget}
            onChange={(e) =>
              setFormData({ ...formData, budget: e.target.value })
            }
            className="border rounded p-2 w-full"
          />
        </div>

        <div className="col-span-2">
          <label className="text-sm text-gray-600">Description</label>
          <textarea
            value={formData.description}
            onChange={(e) =>
              setFormData({ ...formData, description: e.target.value })
            }
            className="border rounded p-2 w-full"
            rows="2"
          />
        </div>

        <div className="col-span-2 flex justify-end gap-2 mt-2">
          {editingCategory && (
            <button
              type="button"
              onClick={onCancel}
              className="bg-gray-300 px-4 py-2 rounded"
            >
              Cancel
            </button>
          )}
          <button
            type="submit"
            className="bg-green-600 text-white px-4 py-2 rounded"
          >
            {editingCategory ? "Update" : "Add"}
          </button>
        </div>
      </form>
    </div>
  );
}

// helper: flatten categories for dropdown
function flattenCategories(cat, depth = 0) {
  const prefix = "— ".repeat(depth);
  let flat = [{ uid: cat.uid, name: cat.name, indent: prefix }];
  if (cat.children) {
    for (const child of cat.children) {
      flat = flat.concat(flattenCategories(child, depth + 1));
    }
  }
  return flat;
}
