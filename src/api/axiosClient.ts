import axios from "axios";

const axiosInstance = axios.create({
  baseURL: "https://raw.githubusercontent.com/Aebel-Shajan/year-in-data/refs/heads/json-data/",
  // baseURL: "https://year-in-data.onrender.com/",
  // baseURL: "http://127.0.0.1:8000/",
  timeout: 5000, // Set a timeout of 5 seconds
  headers: {
    "Content-Type": "application/json",
  },
});

// Export a function to fetch data
export const fetchData = async <T>(url: string): Promise<T> => {
  const response = await axiosInstance.get<T>(url + ".json");
  return response.data;
};
