import { useState } from "react";
import { useNavigate } from "react-router-dom";
import './Login.css';

function Login() {
    const navigate = useNavigate();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // Add authentication logic here
        navigate('/dashboard');
    };

    return (
        <div className="login-container">
            <div className="login-card">
                {/* Logo */}
                <div className="login-logo">
                    <img src="/wolfLogo.png" alt="SafeBites Logo" className="login-logo-img" />
                    <h1>SafeBites</h1>
                </div>

                <h2 className="login-title">Welcome Back</h2>
                <p className="login-subtitle">Login to your account</p>

                {/* Login Form */}
                <form className="login-form" onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="username">Username</label>
                        <input 
                            type="text" 
                            id="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Enter your username"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input 
                            type="password" 
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter your password"
                            required
                        />
                    </div>

                    <a href="#" className="forgot-password">Forgot Password?</a>

                    <button type="submit" className="login-btn">
                        Login
                    </button>
                </form>

                {/* Sign Up Link */}
                <div className="signup-prompt">
                    <p>Don't have an account? <a href="#" onClick={() => navigate('/signup')}>Sign Up</a></p>
                </div>
            </div>
        </div>
    )
}

export default Login;