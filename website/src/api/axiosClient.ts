import axios from "axios";

export const axiosInstance = axios.create({
  // baseURL: "https://aebelshajan.pythonanywhere.com/",
  // baseURL: "http://localhost:8000/",
  // baseURL: "http://67.205.140.3:8000",
  // baseURL: "https://ydapi.uk/",
  baseURL: "/year-in-data/assets/",
  // timeout: 5000, // Set a timeout of 5 seconds
  // headers: {
  //   "Content-Type": "application/json",
  // },
  // withCredentials: true
});

// Export a function to fetch data
export const fetchData = async <T>(url: string): Promise<T> => {
  const response = await axiosInstance.get<T>(url);
  return response.data;
};

export const postData = async <T> (endpoint: string): Promise<T> => {
  const response = await axiosInstance.post(endpoint)
  return response.data
}