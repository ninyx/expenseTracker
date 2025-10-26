import React, { useEffect, useState } from "react";

// Recursive category node with enhanced UI
const CategoryNode = ({ category, depth = 0, onEdit, onDelete }) => {
  const [expanded, setExpanded] = useState(true);
  const hasChildren = category.children?.length > 0;
  
  const percentage = category.budget 
    ? ((category.budget_used || 0) / category.budget) * 100 
    : 0;
  
  const getProgressColor = (pct) => {
    if (pct >= 100) return "bg-red-500";
    if (pct >= 80) return "bg-yellow-500";
    if (pct >= 60) return "bg-orange-500";
    return "bg-green-500";
  };

  const getTypeStyle = (type) => {
    return type === "income"
      ? "bg-green-100 text-green-700 border-green-200"
      : "bg-red-100 text-red-700 border-red-200";
  };

  const getFrequencyIcon = (freq) => {
    const icons = {
      monthly: "📅",
      weekly: "📆",
      yearly: "🗓️",
      "one-time": "⏱️"
    };
    return icons[freq] || "📋";
  };

  return (
    <div className={`${depth > 0 ? 'ml-8 mt-2' : 'mt-3'}`}>
      <div className="bg-white rounded-lg shadow-md border hover:shadow-lg transition-all overflow-hidden">
        {/* Header Section */}
        <div className="p-4 bg-gradient-to-r from-gray-50 to-white border-b">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 flex-1">
              {hasChildren && (
                <button
                  onClick={() => setExpanded(!expanded)}
                  className="text-xl text-blue-600 hover:text-blue-800 transition-colors"
                >
                  {expanded ? "▼" : "▶"}
                </button>
              )}
              {!hasChildren && <div className="w-6"></div>}
              
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1 flex-wrap">
                  <h3 className="font-semibold text-lg text-gray-800">
                    {category.name}
                  </h3>
                  <span className={`text-xs px-2 py-1 rounded-full border font-medium capitalize ${getTypeStyle(category.transaction_type)}`}>
                    {category.transaction_type}
                  </span>
                  <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full font-medium flex items-center gap-1">
                    {getFrequencyIcon(category.frequency)}
                    {category.frequency}
                  </span>
                </div>
                {category.description && (
                  <p className="text-sm text-gray-600">{category.description}</p>
                )}
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => onEdit(category)}
                  className="bg-blue-500 text-white px-3 py-1.5 rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium"
                >
                  ✏️ Edit
                </button>
                <button
                  onClick={() => onDelete(category.uid)}
                  className="bg-red-500 text-white px-3 py-1.5 rounded-lg hover:bg-red-600 transition-colors text-sm font-medium"
                >
                  🗑️
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Budget Section */}
        {category.budget > 0 && (
          <div className="p-4 bg-gray-50">
            <div className="grid grid-cols-3 gap-4 mb-3">
              <div className="bg-white p-3 rounded-lg border">
                <p className="text-xs text-gray-600 mb-1">Budget</p>
                <p className="text-lg font-bold text-blue-700">₱{category.budget.toLocaleString()}</p>
              </div>
              <div className="bg-white p-3 rounded-lg border">
                <p className="text-xs text-gray-600 mb-1">Used</p>
                <p className="text-lg font-bold text-purple-700">₱{(category.budget_used || 0).toLocaleString()}</p>
              </div>
              <div className="bg-white p-3 rounded-lg border">
                <p className="text-xs text-gray-600 mb-1">Remaining</p>
                <p className={`text-lg font-bold ${(category.budget - (category.budget_used || 0)) < 0 ? 'text-red-700' : 'text-green-700'}`}>
                  ₱{(category.budget - (category.budget_used || 0)).toLocaleString()}
                </p>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="mb-2">
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm text-gray-600">Progress</span>
                <span className="text-sm font-semibold text-gray-800">{percentage.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  className={`h-3 rounded-full transition-all duration-500 ${getProgressColor(percentage)}`}
                  style={{ width: `${Math.min(percentage, 100)}%` }}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Children */}
      {expanded && hasChildren && (
        <div className="mt-2 border-l-2 border-gray-300 pl-2">
          {category.children.map((child) => (
            <CategoryNode
              key={child.uid}
              category={child}
              depth={depth + 1}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// Enhanced Form Component
const CategoriesForm = ({ categories, onSubmit, editingCategory, onCancel }) => {
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

  const handleSubmit = () => {
    if (!formData.name) return;
    
    const payload = {
      ...formData,
      budget: formData.budget ? parseFloat(formData.budget) : 0,
      parent_uid: formData.parent_uid || null,
    };
    onSubmit(payload);
  };

  const flattenCategories = (cat, depth = 0) => {
    const prefix = "— ".repeat(depth);
    let flat = [{ uid: cat.uid, name: cat.name, indent: prefix }];
    if (cat.children) {
      for (const child of cat.children) {
        flat = flat.concat(flattenCategories(child, depth + 1));
      }
    }
    return flat;
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-lg border mb-6">
      <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
        {editingCategory ? "✏️ Edit Category" : "➕ Add New Category"}
      </h2>

      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category Name *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="e.g., Groceries"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Transaction Type *
            </label>
            <select
              value={formData.transaction_type}
              onChange={(e) => setFormData({ ...formData, transaction_type: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="expense">💸 Expense</option>
              <option value="income">💰 Income</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Parent Category
            </label>
            <select
              value={formData.parent_uid}
              onChange={(e) => setFormData({ ...formData, parent_uid: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">— None (Top Level) —</option>
              {categories.flatMap(flattenCategories).map((c) => (
                <option key={c.uid} value={c.uid}>
                  {c.indent + c.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Frequency
            </label>
            <select
              value={formData.frequency}
              onChange={(e) => setFormData({ ...formData, frequency: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="monthly">📅 Monthly</option>
              <option value="weekly">📆 Weekly</option>
              <option value="yearly">🗓️ Yearly</option>
              <option value="one-time">⏱️ One-time</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Budget Amount (₱)
            </label>
            <input
              type="number"
              step="0.01"
              value={formData.budget}
              onChange={(e) => setFormData({ ...formData, budget: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="0.00"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description (Optional)
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              rows="2"
              placeholder="Add notes about this category..."
            />
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t">
          {editingCategory && (
            <button
              onClick={onCancel}
              className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
            >
              Cancel
            </button>
          )}
          <button
            onClick={handleSubmit}
            className="px-6 py-2 bg-gradient-to-r from-green-600 to-green-500 text-white rounded-lg hover:from-green-700 hover:to-green-600 transition-colors font-medium shadow-md"
          >
            {editingCategory ? "✓ Update Category" : "➕ Add Category"}
          </button>
        </div>
      </div>
    </div>
  );
};

// Main Component - Replace your Categories.jsx with this
export default function Categories() {
  const [categories, setCategories] = useState([]);
  const [editingCategory, setEditingCategory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState("all");

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      // Import your actual API service
      const { getCategoryTree } = await import('../services/categories');
      const data = await getCategoryTree();
      setCategories(data);
    } catch (err) {
      console.error("Error fetching categories:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (uid) => {
    if (!confirm("Delete this category and all subcategories?")) return;
    try {
      const { deleteCategory } = await import('../services/categories');
      await deleteCategory(uid);
      fetchCategories();
    } catch (err) {
      console.error("Error deleting category:", err);
    }
  };

  const handleSubmit = async (data) => {
    try {
      const { createCategory, updateCategory } = await import('../services/categories');
      
      if (editingCategory) {
        await updateCategory(editingCategory.uid, data);
      } else {
        await createCategory(data);
      }
      setEditingCategory(null);
      fetchCategories();
    } catch (err) {
      console.error("Error saving category:", err);
    }
  };

  const filteredCategories = categories.filter(cat => {
    if (filterType === "all") return true;
    return cat.transaction_type === filterType;
  });

  const calculateStats = () => {
    const countCategories = (cats) => {
      let count = cats.length;
      cats.forEach(cat => {
        if (cat.children) count += countCategories(cat.children);
      });
      return count;
    };

    const sumBudgets = (cats) => {
      let sum = 0;
      cats.forEach(cat => {
        sum += cat.budget || 0;
        if (cat.children) sum += sumBudgets(cat.children);
      });
      return sum;
    };

    return {
      total: countCategories(categories),
      income: countCategories(categories.filter(c => c.transaction_type === "income")),
      expense: countCategories(categories.filter(c => c.transaction_type === "expense")),
      totalBudget: sumBudgets(categories)
    };
  };

  const stats = calculateStats();

  if (loading) {
    return <div className="p-6 text-center text-gray-500">Loading categories...</div>;
  }

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-2">
            📂 Categories
          </h1>
          <p className="text-gray-600 mt-1">Organize and track your income and expenses</p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-xl p-6 shadow-lg">
          <div className="text-3xl mb-2">📊</div>
          <p className="text-sm opacity-90">Total Categories</p>
          <p className="text-3xl font-bold">{stats.total}</p>
        </div>
        <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-xl p-6 shadow-lg">
          <div className="text-3xl mb-2">💰</div>
          <p className="text-sm opacity-90">Income Categories</p>
          <p className="text-3xl font-bold">{stats.income}</p>
        </div>
        <div className="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-xl p-6 shadow-lg">
          <div className="text-3xl mb-2">💸</div>
          <p className="text-sm opacity-90">Expense Categories</p>
          <p className="text-3xl font-bold">{stats.expense}</p>
        </div>
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-xl p-6 shadow-lg">
          <div className="text-3xl mb-2">💵</div>
          <p className="text-sm opacity-90">Total Budget</p>
          <p className="text-3xl font-bold">₱{stats.totalBudget.toLocaleString()}</p>
        </div>
      </div>

      {/* Form */}
      <CategoriesForm
        onSubmit={handleSubmit}
        editingCategory={editingCategory}
        onCancel={() => setEditingCategory(null)}
        categories={categories}
      />

      {/* Filter */}
      <div className="flex gap-2 items-center bg-white p-4 rounded-lg shadow-md border">
        <span className="text-sm font-medium text-gray-700">Filter:</span>
        <button
          onClick={() => setFilterType("all")}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filterType === "all"
              ? "bg-blue-600 text-white"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
        >
          All
        </button>
        <button
          onClick={() => setFilterType("income")}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filterType === "income"
              ? "bg-green-600 text-white"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
        >
          💰 Income
        </button>
        <button
          onClick={() => setFilterType("expense")}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filterType === "expense"
              ? "bg-red-600 text-white"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
        >
          💸 Expense
        </button>
      </div>

      {/* Categories List */}
      <div>
        {filteredCategories.length === 0 ? (
          <div className="bg-white rounded-lg p-12 text-center border shadow-sm">
            <div className="text-6xl mb-4">📂</div>
            <p className="text-lg font-medium text-gray-700 mb-2">No Categories Found</p>
            <p className="text-gray-500">Create your first category to get started organizing your finances</p>
          </div>
        ) : (
          filteredCategories.map((cat) => (
            <CategoryNode
              key={cat.uid}
              category={cat}
              onEdit={setEditingCategory}
              onDelete={handleDelete}
            />
          ))
        )}
      </div>
    </div>
  );
}