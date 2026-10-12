import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";
import AuroraBackground from "./AuroraBackground";

function Login() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = (e) => {
    e.preventDefault();

    if (username === "admin" && password === "admin123") {
      localStorage.setItem("isLoggedIn", "true");
      navigate("/dashboard");
    } else {
      alert("Invalid Username or Password");
    }
  };

  return (
    <>
      <AuroraBackground />

      <div className="login-page">
        <div className="login-card">

          <div className="logo">
            <h1>SQLSphere</h1>
            <p>Conversational SQL Assistant</p>
          </div>

          <p className="subtitle">
            Conversational SQL Assistant
          </p>

          <form onSubmit={handleLogin}>

            <div className="input-group">
              <label>Username</label>

              <input
                type="text"
                placeholder="Enter username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>

            <div className="input-group">
              <label>Password</label>

              <input
                type="password"
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <div className="options">
              <label>
                <input type="checkbox" />
                {" "}Remember Me
              </label>

              <a href="/">Forgot Password?</a>
            </div>

            <button
              type="submit"
              className="login-btn"
            >
              Sign In →
            </button>

          </form>

          <div className="footer">
            © 2026 SQLSphere
          </div>

        </div>
      </div>
    </>
  );
}

export default Login;