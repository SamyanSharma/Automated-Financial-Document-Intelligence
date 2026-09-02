import axios from "axios";

const API = axios.create({
    baseURL: "http://127.0.0.1:8000"
});

export const analyzeCompany = async (companyName) => {
    const response = await API.get(
        `/api/v1/analysis/company/${encodeURIComponent(companyName)}`
    );

    return response.data;
};

export default API;