import api from "./api";

export const getTransactions = async () => {
  const res = await api.get("/transactions");
  return res.data;
};

export const getTransactionById = async (id) => {
  const res = await api.get(`/transactions/${id}`);
  return res.data;
}

export const updateTransaction = async (id, data) => {
  const res = await api.put(`/transactions/${id}`, data);
  return res.data;
};

export const createTransaction = async (data) => {
  const res = await api.post("/transactions", data);
  return res.data;
};

export const deleteTransaction = async (id) => {
  const res = await api.delete(`/transactions/${id}`);
  return res.data;
};
