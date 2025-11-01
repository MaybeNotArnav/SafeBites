import { useState } from "react";
import { useNavigate } from "react-router-dom";
import './SignUp.css';

function SignUp() {
    const navigate = useNavigate();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // Add validation and registration logic here
        if (password !== confirmPassword) {
            alert("Passwords don't match!");
            return;
        }
        if (password.length < 6) {
            alert("Password must be at least 6 characters!");
            return;
        }
        // Navigate to dashboard after successful signup
        navigate('/dashboard');
    };

    return (
        <div className="signup-container">
            <div className="signup-card">
                {/* Logo */}
                <div className="signup-logo">
                    <img src="/wolfLogo.png" alt="SafeBites Logo" className="signup-logo-img" />
                    <h1>SafeBites</h1>
                </div>

                <h2 className="signup-title">Create Account</h2>
                <p className="signup-subtitle">Join SafeBites today</p>

                {/* Sign Up Form */}
                <form className="signup-form" onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="username">Username</label>
                        <input 
                            type="text" 
                            id="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Choose a username"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Create Password</label>
                        <input 
                            type="password" 
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Create a strong password"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="confirmPassword">Confirm Password</label>
                        <input 
                            type="password" 
                            id="confirmPassword"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            placeholder="Confirm your password"
                            required
                        />
                    </div>

                    <button type="submit" className="signup-btn">
                        Sign Up
                    </button>
                </form>

                {/* Login Link */}
                <div className="login-prompt">
                    <p>Already have an account? <a href="#" onClick={(e) => { e.preventDefault(); navigate('/login'); }}>Login</a></p>
                </div>
            </div>
        </div>
    );
}

export default SignUp;