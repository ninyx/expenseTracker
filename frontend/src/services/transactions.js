import api from "./api";

export const getTransactions = async () => {
  const response = await api.get("/transactions/");
  return response.data;
};

export const getTransactionById = async (uid) => {
  const response = await api.get(`/transactions/${uid}`);
  return response.data;
}

export const createTransaction = async (data) => {
  const response = await api.post("/transactions/", data);
  return response.data;
};

export const updateTransaction = async (uid, data) => {
  const response = await api.patch(`/transactions/${uid}`, data);
  return response.data;
};

export const deleteTransaction = async (uid) => {
  const response = await api.delete(`/transactions/${uid}`);
  return response.data;
};
