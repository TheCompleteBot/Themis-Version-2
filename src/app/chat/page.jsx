"use client";
import { useState } from "react";
import ThemisChatBot from "../chat/_components/Chatbot";

export default function GenerateContract() {
  const [formData, setFormData] = useState({
    contract_type: "",
    party1: "",
    party2: "",
    jurisdiction: "",
    additional_jurisdictions: "",
    additional_info: "",
    details: {},
  });
  const [contractId, setContractId] = useState(null); // State for contract ID
  const [message, setMessage] = useState("");
  const [error, setError] = useState(false);
  const [pdfLink, setPdfLink] = useState("");

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleContractTypeChange = (e) => {
    const contract_type = e.target.value;
    setFormData((prev) => ({ ...prev, contract_type, details: {} }));
  };

  const handleDetailsChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      details: { ...prev.details, [name]: value },
    }));
  };

  const getToken = () => {
    return localStorage.getItem("access_token");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setError(false);
    setPdfLink("");

    const token = getToken();
    if (!token) {
      setError(true);
      setMessage("You must be logged in to generate a contract.");
      return;
    }

    const payload = {
      ...formData,
      additional_jurisdictions: formData.additional_jurisdictions
        .split(",")
        .map((item) => item.trim()),
    };

    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/contracts/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      
      if (response.ok && data.completed) {
        console.log(data)
        console.log(data.id)
        setMessage("Contract generated successfully!");
        setPdfLink(`http://127.0.0.1:8000/${data.pdf_file}`);
        setContractId(data.id); // Save contract ID for the chatbot
      } else {
        setError(true);
        setMessage(data.error || "Contract generation failed.");
      }
    } catch (error) {
      setError(true);
      setMessage("An error occurred while generating the contract.");
      console.error("Contract Generation Error:", error);
    }
  };

  return (
    <div className="container mx-auto p-8 bg-gray-50 shadow-lg rounded-lg">
      <h2 className="text-2xl font-bold text-gray-700 mb-6 text-center">
        Generate Contract
      </h2>
      <div className="bg-red-700 w-full">
        <h1>Hello</h1>
        <div>
        {contractId && (
        <div style={{ position: "fixed", bottom: "20px", right: "20px", width: "300px" }}>
          <ThemisChatBot contractId={contractId} />
        </div>
      )}
        </div>
   
        </div>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="contract_type" className="block font-medium text-gray-700">
            Contract Type:
          </label>
          <select
            id="contract_type"
            name="contract_type"
            value={formData.contract_type}
            onChange={handleContractTypeChange}
            required
            className="w-full mt-2 p-2 border border-gray-300 rounded-lg"
          >
            <option value="">Select Type</option>
            <option value="employment">Employment</option>
            <option value="service">Service</option>
            <option value="lease">Lease</option>
            <option value="nda">NDA</option>
          </select>
        </div>

        <div>
          <label htmlFor="party1" className="block font-medium text-gray-700">
            Party 1:
          </label>
          <input
            type="text"
            id="party1"
            name="party1"
            value={formData.party1}
            onChange={handleInputChange}
            required
            className="w-full mt-2 p-2 border border-gray-300 rounded-lg"
          />
        </div>

        <div>
          <label htmlFor="party2" className="block font-medium text-gray-700">
            Party 2:
          </label>
          <input
            type="text"
            id="party2"
            name="party2"
            value={formData.party2}
            onChange={handleInputChange}
            required
            className="w-full mt-2 p-2 border border-gray-300 rounded-lg"
          />
        </div>

        <div>
          <label htmlFor="jurisdiction" className="block font-medium text-gray-700">
            Jurisdiction:
          </label>
          <input
            type="text"
            id="jurisdiction"
            name="jurisdiction"
            value={formData.jurisdiction}
            onChange={handleInputChange}
            required
            className="w-full mt-2 p-2 border border-gray-300 rounded-lg"
          />
        </div>

        <div>
          <label
            htmlFor="additional_jurisdictions"
            className="block font-medium text-gray-700"
          >
            Additional Jurisdictions (comma-separated):
          </label>
          <input
            type="text"
            id="additional_jurisdictions"
            name="additional_jurisdictions"
            value={formData.additional_jurisdictions}
            onChange={handleInputChange}
            className="w-full mt-2 p-2 border border-gray-300 rounded-lg"
          />
        </div>

        {formData.contract_type === "employment" && (
          <div className="space-y-4">
            <div>
              <label htmlFor="position" className="block font-medium text-gray-700">
                Position:
              </label>
              <input
                type="text"
                id="position"
                name="position"
                value={formData.details.position || ""}
                onChange={handleDetailsChange}
                required
                className="w-full mt-2 p-2 border border-gray-300 rounded-lg"
              />
            </div>

            <div>
              <label htmlFor="salary" className="block font-medium text-gray-700">
                Salary:
              </label>
              <input
                type="number"
                id="salary"
                name="salary"
                value={formData.details.salary || ""}
                onChange={handleDetailsChange}
                required
                className="w-full mt-2 p-2 border border-gray-300 rounded-lg"
              />
            </div>

            <div>
              <label htmlFor="start_date" className="block font-medium text-gray-700">
                Start Date:
              </label>
              <input
                type="date"
                id="start_date"
                name="start_date"
                value={formData.details.start_date || ""}
                onChange={handleDetailsChange}
                required
                className="w-full mt-2 p-2 border border-gray-300 rounded-lg"
              />
            </div>
          </div>
        )}

        <div>
          <label htmlFor="additional_info" className="block font-medium text-gray-700">
            Additional Information:
          </label>
          <textarea
            id="additional_info"
            name="additional_info"
            value={formData.additional_info}
            onChange={handleInputChange}
            className="w-full mt-2 p-2 border border-gray-300 rounded-lg"
          />
        </div>

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
        >
          Generate Contract
        </button>
        
      </form>

      {message && (
        <p
          className={`mt-4 text-center font-medium ${
            error ? "text-red-600" : "text-green-600"
          }`}
        >
          {message}
        </p>
      )}

      {pdfLink && (
        <p className="mt-4 text-center">
          <a
            href={pdfLink}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline"
          >
            Download PDF
          </a>
        </p>
      )}

      
    </div>
  );
}
