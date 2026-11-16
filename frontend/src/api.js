import axios from"axios";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    timeout: 10000
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
})


api.interceptors.response.use(
    (res) => res,
    (err) => {
        let errorMsg;
        if (err?.response?.status == 401) {
            localStorage.removeItem('user')
            localStorage.removeItem('token')
            errorMsg = "Please log in to do that";
        }
        else{
            errorMsg = err?.response?.data?.detail;
        }
        err.message = errorMsg;
        return Promise.reject(err);
    }
)

export default api;
