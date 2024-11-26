"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Login() {
  const BASE_URL = "http://127.0.0.1:8000";
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const router = useRouter();

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch(`${BASE_URL}/api/v1/auth/token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({ username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem("access_token", data.access_token);
        setMessage("Login successful! Redirecting...");
        setIsError(false);
        setTimeout(() => {
          router.push("/chat"); // Redirect to the generate_contract page
        }, 1500);
      } else {
        setMessage(data.detail || "Login failed.");
        setIsError(true);
      }
    } catch (error) {
      setMessage("An error occurred during login.");
      setIsError(true);
      console.error("Login Error:", error);
    }
  };

  return (
    <div className="container">
      <h2>Log In</h2>
      <form onSubmit={handleLogin}>
        <label htmlFor="username">Username:</label>
        <input
          type="text"
          id="username"
          name="username"
          required
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <label htmlFor="password">Password:</label>
        <input
          type="password"
          id="password"
          name="password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button type="submit" className="button">
          Log In
        </button>
      </form>
      {message && (
        <p style={{ color: isError ? "red" : "green" }}>{message}</p>
      )}
      <p>
        Don't have an account? <a href="/signup">Sign Up</a>
      </p>
    </div>
  );
}
