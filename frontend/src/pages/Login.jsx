import { useState } from "react";
import { useAuth } from "../auth";
import api from "../api";

import { Modal, Button, Form, Alert } from 'react-bootstrap'

export default function Login({ show, onHide }) {
    const { login } = useAuth();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [errors, setErrors] = useState(null);

    async function handleLogin(e) {
        e.preventDefault();
        setErrors(null);
        try {
            await login(username, password);
            onHide();
            setUsername("")
            setPassword("")
            setErrors("")
        } catch (err) {
            setErrors(err)
        }
    }

    async function handleRegister(e) {
        e.preventDefault();
        try{
            const { data } = await api.post("/register_user", {
                username, password
            });
            handleLogin(e);
        } catch (err) {
            setErrors(err)
        }
    }
    return (
        <Modal show={show} onHide={onHide} centered>
            <Form onSubmit={handleLogin}>
                <Modal.Header closeButton>
                    <Modal.Title>
                        Login
                    </Modal.Title>
                </Modal.Header>

                <Modal.Body>
                    {errors && <Alert variant="danger">{errors?.message}</Alert>}
                    <Form.Group className="mb-3" controlId="loginUsername">
                        <Form.Label>Username</Form.Label>
                        <Form.Control type="text" value={username}
                            onChange={(e) => setUsername(e.target.value)} required autoFocus />
                    </Form.Group>
                    <Form.Group className="mb-3" controlId="loginPassword">
                        <Form.Label>Password</Form.Label>
                        <Form.Control type="password" value={password}
                            onChange={(e) => setPassword(e.target.value)} required />
                    </Form.Group>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={handleRegister}>Register</Button>
                    <p>OR</p>
                    <Button type="submit">Sign In</Button>
                </Modal.Footer>
            </Form>
        </Modal>
    );
}