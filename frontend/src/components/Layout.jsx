import { useState } from 'react';

import { NavLink, Outlet, useNavigate } from 'react-router';
import { Navbar, Nav, Container, Button } from 'react-bootstrap';

import { useAuth } from '../auth';
import Login from '../pages/Login';

export default function Layout() {
    const navigate = useNavigate();
    const { user, logout } = useAuth();
    const [showLogin, setShowLogin] = useState(false);
    return (
        <div className='d-flex flex-column h-100'>
            <Navbar bg="dark" data-bs-theme="dark" expand="md">
                <Container style={{ display: 'flex' }}>
                    <Navbar.Brand style={{ flex: 5 }}>URL Shortener
                        <span className='px-3' style={{
                            letterSpacing: '1.6px',
                            fontSize: '0.6em',
                            fontWeight: "lighter"
                        }}
                        >... because size matters.</span>
                    </Navbar.Brand>
                    <Navbar.Toggle />
                    <Navbar.Collapse style={{ maxWidth: "10em" }}>
                        <Nav className="me-auto">
                            <Nav.Link as={NavLink} to="/">Home</Nav.Link>
                        </Nav>

                        {user ? (
                            <>
                                <Navbar.Text className="me-3">{user.username}</Navbar.Text>
                                <Button variant="outline-light" size="sm"
                                    onClick={() => { logout(); navigate("/"); }}>
                                    Logout
                                </Button>
                            </>
                        ) : (
                            <Nav.Link as="button" onClick={() => setShowLogin(true)}>
                                Login
                            </Nav.Link>
                        )}
                    </Navbar.Collapse>
                </Container>
            </Navbar>

            <Container className="py-4 flex-grow-1">
                <Outlet />
            </Container>

            <Login show={showLogin} onHide={() => setShowLogin(false)} />
        </div>
    );
}