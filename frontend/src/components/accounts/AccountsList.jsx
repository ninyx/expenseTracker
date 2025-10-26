import { useState } from "react";

export default function AccountList({ accounts, onDelete, onUpdate }) {
  const [editingId, setEditingId] = useState(null);
  const [editedData, setEditedData] = useState({ name: "", type: "" });

  const startEdit = (acc) => {
    setEditingId(acc.uid);
    setEditedData({ name: acc.name, type: acc.type });
  };

  const cancelEdit = () => setEditingId(null);

  const saveEdit = (uid) => {
    onUpdate(uid, editedData);
    setEditingId(null);
  };

  if (!accounts.length) {
    return <p className="text-gray-500 italic">No accounts found.</p>;
  }

  return (
    <ul className="space-y-3">
      {accounts.map((acc) => (
        <li
          key={acc.uid}
          className="border rounded-lg p-4 shadow-sm flex justify-between items-center"
        >
          {editingId === acc.uid ? (
            <div className="flex-1 space-y-1">
              <input
                className="border p-1 rounded-md w-full"
                value={editedData.name}
                onChange={(e) =>
                  setEditedData((prev) => ({ ...prev, name: e.target.value }))
                }
              />
              <select
                className="border p-1 rounded-md w-full"
                value={editedData.type}
                onChange={(e) =>
                  setEditedData((prev) => ({ ...prev, type: e.target.value }))
                }
              >
                <option value="cash">Cash</option>
                <option value="bank">Bank</option>
                <option value="credit">Credit</option>
                <option value="investment">Investment</option>
                <option value="other">Other</option>
              </select>
              <div className="space-x-2 mt-1">
                <button
                  onClick={() => saveEdit(acc.uid)}
                  className="text-green-600 font-medium"
                >
                  Save
                </button>
                <button
                  onClick={cancelEdit}
                  className="text-gray-500 font-medium"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <>
              <div>
                <p className="font-semibold">{acc.name}</p>
                <p className="text-sm text-gray-500 capitalize">{acc.type}</p>
              </div>
              <div className="flex items-center gap-2">
                <p className="font-bold text-blue-600">
                  ₱{acc.balance.toLocaleString()}
                </p>
                <button
                  onClick={() => startEdit(acc)}
                  className="text-sm text-blue-500 hover:underline"
                >
                  Edit
                </button>
                <button
                  onClick={() => onDelete(acc.uid)}
                  className="text-sm text-red-500 hover:underline"
                >
                  Delete
                </button>
              </div>
            </>
          )}
        </li>
      ))}
    </ul>
  );
}
