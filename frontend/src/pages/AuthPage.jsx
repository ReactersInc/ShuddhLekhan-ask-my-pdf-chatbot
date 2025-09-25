import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./AuthPage.css";
import { Eye, EyeOff } from "lucide-react";

const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    // If user is already logged in, redirect to dashboard
    const token = localStorage.getItem('token');
    if (token) {
      navigate('/dashboard');
    }
  }, [navigate]);

  const togglePassword = () => setShowPassword((prev) => !prev);

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    const endpoint = isLogin ? "/auth/login" : "/auth/signup"; // Fixed endpoint paths
    const payload = isLogin
      ? { email: form.email, password: form.password }
      : form;

    try {
      const res = await fetch(`http://localhost:5000${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (res.ok && data.token) {
        localStorage.setItem("token", data.token);
        localStorage.setItem("user", JSON.stringify(data.user));
        navigate("/dashboard");
      } else {
        setError(data?.message || data?.error || "Something went wrong");
      }
    } catch (err) {
      setError("Network error - Please check if the server is running");
    }
  };

  // I am keeping this for future , We may Shift to SUPABASE Auth to implement OAuth
  // This will redirect to Flask OAuth route when implemented and Flask Server will redirect to the Actual URL

  const handleGoogleLogin = () => {
    window.location.href = "http://localhost:5000/api/oauth/google";
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>{isLogin ? "Login to ShudhLeekan" : "Create an Account"}</h2>

        {error && <p className="error">{error}</p>}

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <div className="form-group">
              <label>Name</label>
              <input
                name="name"
                type="text"
                placeholder="Your Name"
                value={form.name}
                onChange={handleChange}
                required
              />
            </div>
          )}
          <div className="form-group">
            <label>Email</label>
            <input
              name="email"
              type="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <div className="password-wrapper">
              <input
                name="password"
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                value={form.password}
                onChange={handleChange}
                required
              />
              <span onClick={togglePassword}>
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </span>
            </div>
          </div>

          <button type="submit">{isLogin ? "Login" : "Sign Up"}</button>
        </form>

        <button onClick={handleGoogleLogin} className="google-btn">
          <img
            src="https://www.svgrepo.com/show/475656/google-color.svg"
            alt="Google"
            className="google-icon"
          />
          Continue with Google
        </button>

        <p className="toggle-text">
          {isLogin ? "Don't have an account?" : "Already have an account?"}{" "}
          <span onClick={() => setIsLogin((prev) => !prev)}>
            {isLogin ? "Sign Up" : "Login"}
          </span>
        </p>
      </div>
    </div>
  );
};

export default AuthPage;
