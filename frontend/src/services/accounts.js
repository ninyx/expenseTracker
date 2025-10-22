import api from "./api";

// GET /accounts
export const getAccounts = async () => {
  const res = await api.get("/accounts/");
  return res.data;
};

// GET /accounts/{uid}
export const getAccountById = async (uid) => {
  const res = await api.get(`/accounts/${uid}`);
  return res.data;
};

// POST /accounts
export const createAccount = async (accountData) => {
  const res = await api.post("/accounts/", accountData);
  return res.data;
};

// PATCH /accounts/{uid}
export const updateAccount = async (uid, accountData) => {
  const res = await api.patch(`/accounts/${uid}`, accountData);
  return res.data;
};

// DELETE /accounts/{uid}
export const deleteAccount = async (uid) => {
  const res = await api.delete(`/accounts/${uid}`);
  return res.data;
};
