import { useNavigate } from "react-router-dom";
import './SignUp.css';

function SignUp() {
    const navigate = useNavigate();
    return (
        <div className="signup-container">
            <div className="signup-card">
                <h1>Sign Up Page</h1>
                <p>This page is under construction.</p>
                <button className="temp-signup-btn" onClick={() => navigate('/login')}>
                    Go to Login (Temporary)
                </button>
            </div>
        </div>
    );
}
export default SignUp;