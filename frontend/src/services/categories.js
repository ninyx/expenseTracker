import api from "./api";

// Create
export const createCategory = async (data) => {
  const res = await api.post("/categories", data);
  return res.data;
};

// Get all (flat)
export const getCategories = async () => {
  const res = await api.get("/categories");
  return res.data;
};

// Get tree (hierarchical)
export const getCategoryTree = async () => {
  const res = await api.get("/categories/tree");
  return res.data;
};

export const getCategory = async (uid) => {
  const res = await api.get(`/categories/${uid}`);
  return res.data;
};

// Update (generic)
export const updateCategory = async (uid, data) => {
  const res = await api.patch(`/categories/${uid}`, data);
  return res.data;
};

// Delete
export const deleteCategory = async (uid) => {
  const res = await api.delete(`/categories/${uid}`);
  return res.data;
};
