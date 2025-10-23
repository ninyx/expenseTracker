// src/pages/Categories.jsx
import React, { useEffect, useState } from "react";
import {
  getCategoryTree,
  createCategory,
  updateCategory,
  deleteCategory,
} from "../services/categories";
import toast from "react-hot-toast";
import CategoriesForm from "../components/CategoriesForm.jsx";

// Recursive category node display
const CategoryNode = ({ category, onEdit, onDelete }) => {
  const [expanded, setExpanded] = useState(true);

  return (
    <div className="border-l pl-3 mt-2">
      <div className="flex justify-between items-center py-1">
        <div className="flex items-center gap-2">
          {category.children?.length > 0 && (
            <button
              className="text-sm text-blue-600"
              onClick={() => setExpanded(!expanded)}
            >
              {expanded ? "▼" : "▶"}
            </button>
          )}
          <span className="font-medium">{category.name}</span>
          <span className="text-gray-500 text-sm">
            ({category.transaction_type})
          </span>
        </div>

        <div className="flex items-center gap-3 text-sm">
          <span className="text-gray-700">
            ₱{(category.budget ?? 0).toLocaleString()}
          </span>
          <button
            onClick={() => onEdit(category)}
            className="bg-yellow-400 text-white text-xs px-2 py-1 rounded"
          >
            ✏️
          </button>
          <button
            onClick={() => onDelete(category.uid)}
            className="bg-red-500 text-white text-xs px-2 py-1 rounded"
          >
            🗑️
          </button>
        </div>
      </div>

      {expanded &&
        category.children &&
        category.children.map((child) => (
          <CategoryNode
            key={child.uid}
            category={child}
            onEdit={onEdit}
            onDelete={onDelete}
          />
        ))}
    </div>
  );
};

export default function Categories() {
  const [categories, setCategories] = useState([]);
  const [editingCategory, setEditingCategory] = useState(null);

  const fetchCategories = async () => {
    try {
      const data = await getCategoryTree();
      setCategories(data);
    } catch (err) {
      console.error("Error fetching categories:", err);
      toast.error("Failed to load categories");
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  const handleDelete = async (uid) => {
    if (!confirm("Delete this category?")) return;
    try {
      await deleteCategory(uid);
      toast.success("Category deleted!");
      fetchCategories();
    } catch {
      toast.error("Delete failed");
    }
  };

  const handleSubmit = async (data) => {
    try {
      if (editingCategory) {
        await updateCategory(editingCategory.uid, data);
        toast.success("Category updated!");
      } else {
        await createCategory(data);
        toast.success("Category created!");
      }
      setEditingCategory(null);
      fetchCategories();
    } catch (err) {
      console.error(err);
      toast.error("Failed to save category");
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold mb-4">📂 Categories</h1>

      <CategoriesForm
        onSubmit={handleSubmit}
        editingCategory={editingCategory}
        onCancel={() => setEditingCategory(null)}
        categories={categories}
      />

      <div className="mt-6">
        {categories.length === 0 ? (
          <p className="text-gray-500">No categories yet.</p>
        ) : (
          categories.map((cat) => (
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
