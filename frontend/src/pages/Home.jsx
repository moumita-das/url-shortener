import { useState, useEffect } from 'react';

import api from '../api';
import { useAuth } from '../auth';

import { Button, ButtonGroup, Form, Container, Row, Col, Alert } from 'react-bootstrap'

// Everything that differs between the two lookups, in one place: which
// endpoint to call, what the query parameter is named, and which key the
// answer comes back under. The backend uses a different word in all three
// slots, which is what makes this easy to get wrong.
// "short" uses /generate_url because that endpoint already returns an
// existing mapping when the long URL has been shortened before, and only
// creates a new one otherwise — which is exactly "fetch me a short URL".
const ACTIONS = {
    short: { endpoint: "/generate_url", param: "long_url" },
    long: { endpoint: "/get_long_url", param: "short_url" },
};

const Home = () => {
    const [providedURL, setProvidedURL] = useState("");
    const [fetchedURL, setfetchedURL] = useState("");
    const [tilt, setTilt] = useState(0);
    const [actionType, setActionType] = useState(null);
    const [error, setError] = useState(null);
    const { user } = useAuth();

    const handleFetchUrl = async (type) => {
        if (!providedURL.trim()) return;

        const { endpoint, param } = ACTIONS[type];

        try {
            const { data } = await api.get(endpoint, {
                params: { [param]: providedURL }
            });
            setfetchedURL(data['url'] ?? "");
            setActionType(type);
        } catch (err) {
            setError(err.message);
            setfetchedURL("");
        }
    }

    const handleDelete = async () => {
        // After "fetch short" the short URL is the result; after "fetch long"
        // it is what the user typed in.
        const shortURL = actionType === "short" ? fetchedURL : providedURL;
        if (!shortURL.trim()) return;

        try {
            await api.delete("/delete_url", {
                params: { short_url: shortURL }
            });
            setProvidedURL("");
            setfetchedURL("");
            setActionType(null);
        } catch (err) {
            setError(err.message);
        }
    }

    useEffect(() => {
        if (providedURL.trim() == "") {
            setTilt(0);
            setfetchedURL("");
        }
        else {
            if (actionType == 'long')
                setTilt(6);
            else if (actionType == 'short')
                setTilt(-6);
            else
                setTilt(0);
        }

    }, [actionType, providedURL])

    return (
        <Container className='h-100'>
            <Row className='align-items-end ground' style={{ height: '70%' }}>
                <Col>
                    <ButtonGroup vertical>
                        <Button className='action-btn' active={actionType == "short"} onClick={() => handleFetchUrl('short')}>
                            Fetch Short URL
                        </Button>
                        <Button className='action-btn' active={actionType == "long"} onClick={() => handleFetchUrl('long')}>
                            Fetch Long URL
                        </Button>
                        {user && (
                            <Button className='action-btn' onClick={() => handleDelete()} >
                                Delete
                            </Button>
                        )}
                    </ButtonGroup>
                </Col>
                <Col style={{ flex: '4' }}>
                    <div className='see-saw' style={{ '--tilt': `${tilt}deg` }}>
                        <div className='beam' >
                            <div className='rod'>
                                <Form.Control
                                    name="provided-url-input"
                                    className='url-input'
                                    placeholder='Enter URL'
                                    value={providedURL}
                                    onChange={(e) => setProvidedURL(e.target.value)}
                                />
                                <Form.Control
                                    name="fetched-url-input"
                                    className='url-input'
                                    value={fetchedURL}
                                    readOnly
                                />
                            </div>
                        </div>
                        <div className='fulcrum' />
                    </div>
                </Col>

            </Row>
            {error && <div className="mt-3 d-flex justify-content-center" style={{
                color: '#ab2432'
            }}><p>{error}</p></div>}
        </Container>
    )
}

export default Home;