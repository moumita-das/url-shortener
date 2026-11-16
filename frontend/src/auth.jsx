import { createContext, useContext, useState } from "react";

import api from "./api";

const AuthContext = createContext(null)

export function AuthProvidor({children}) {
    const [user, setUser] = useState(() => {
        const saved = localStorage.getItem('user');
        return saved ? JSON.parse(saved) : null;
    });

    async function login (username, password) {
        try {
            const { data } = await api.post("/login", new URLSearchParams({ username, password }));
            localStorage.setItem('token', data.access_token);
            const { user } = data;
            setUser(user)
            localStorage.setItem('user', JSON.stringify(user));

        } catch (err) {
            throw err;
        }
        
    }

    function logout() {
        setUser(null);
        localStorage.removeItem('user');
    }

    return (
        <AuthContext.Provider value={{ user, login, logout}}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext)

