import { useNavigate } from "react-router-dom";
import './Login.css';

function Login() {
    const navigate = useNavigate();

    return (
        <div className="login-container">
            <div className="login-card">
                <h1>Login Page</h1>
                <p>This page is under construction.</p>
                <button className="temp-login-btn" onClick={() => navigate('/dashboard')}>
                    Go to Dashboard (Temporary)
                </button>
            </div>
        </div>
    )
}

export default Login;