"use client";

import { useRouter } from "next/navigation";

export default function LandingPage() {
  const router = useRouter(); // eslint-disable-next-line @typescript-eslint/no-unused-vars


  const handleGoogleLogin = () => {
    console.log("Logging in with Google...");
    router.push("/login"); // Navigate to the chat page
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <header className="mb-10 text-center">
        <h1 className="text-4xl font-bold text-gray-800">Themis Welcomes You</h1>
        <p className="text-gray-600 mt-4">Your AI assistant at your fingertips.</p>
      </header>
      <main>
        <button
          onClick={handleGoogleLogin}
          className="px-6 py-3 bg-blue-500 text-white rounded-lg shadow-md hover:bg-blue-600 focus:outline-none"
        >
          Login
        </button>
      </main>
    </div>
  );
}
