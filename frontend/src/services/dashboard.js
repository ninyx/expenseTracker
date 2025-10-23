// src/services/dashboard.js
import axios from "axios";

const BASE_URL = "http://localhost:8000/api";

export const getAccounts = async () => {
  const res = await axios.get(`${BASE_URL}/accounts`);
  return res.data;
};

export const getTransactions = async () => {
  const res = await axios.get(`${BASE_URL}/transactions`);
  return res.data;
};

export const getCategories = async () => {
  const res = await axios.get(`${BASE_URL}/categories/tree`);
  return res.data;
};
