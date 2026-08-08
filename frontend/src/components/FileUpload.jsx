import React, { useState } from "react"
import axios from "axios"
import LoadingSpinner from "./LoadingSpinner"
import ResultCard from "./ResultCard"
import { useNavigate} from "react-router-dom"

const FileUpload = () => {
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const navigate = useNavigate()

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  }

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file");
      return;
    }

    try {
      setLoading(true);

      const formData = new FormData();

      formData.append("file", file);

      const response = await axios.post(
        "https://legalsathi-v2-backend.onrender.com/api/upload/",
        formData
      )

      setResult(response.data);
    } catch (error) {
      console.log(error);
      alert("Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className="min-h-screen bg-[#F7F1E5] flex items-center justify-center px-6 py-12 relative "
      style={{ fontFamily: "'Inter', system-ui, sans-serif" }}
    >
      <button
        className="absolute top-6 left-6 bg-[#F7F1E5] border border-[#DDD0B3] text-[#2E2A22] px-4 py-2 rounded-lg shadow-sm hover:bg-[#EDE2CC] transition-colors"
        onClick={()=>navigate(-1)}>
        Back
      </button>

      <div className="w-full max-w-2xl bg-[#EDE2CC] border border-[#DDD0B3] shadow-xl rounded-3xl p-8">

        <h1
          className="text-4xl font-semibold text-center text-[#2F4A3B] mb-3"
          style={{ fontFamily: "'Fraunces', serif" }}
        >
          Upload Your Legal Document
        </h1>

        <p className="text-center text-[#6B6353] mb-8">
          Upload a PDF or image and get an AI-powered legal explanation.
        </p>

        <input
          type="file"
          onChange={handleFileChange}
          className="w-full border-2 border-dashed border-[#B8933F] rounded-xl p-4 cursor-pointer bg-[#F7F1E5] hover:bg-[#F1E8D4] transition duration-300 text-[#4A4436]"
        />

        {file && (
          <div className="mt-5 bg-[#F7F1E5] border border-[#2F4A3B]/30 rounded-xl p-4">
            <p className="text-[#2F4A3B] font-medium">
               Selected File:
            </p>

            <p className="text-[#4A4436] mt-1 break-all">
              {file.name}
            </p>
          </div>
        )}

        <button
          onClick={handleUpload}
          className="w-full mt-8 bg-[#2F4A3B] hover:bg-[#25392F] text-[#F7F1E5] text-lg font-semibold py-4 rounded-xl shadow-lg transition duration-300 cursor-pointer"
        >
          Upload Document
        </button>

        {loading && (
          <div className="mt-8 flex justify-center">
            <LoadingSpinner />
          </div>
        )}

        {result && (
          <div className="mt-8">
            <ResultCard result={result} />
          </div>
        )}
      </div>
    </div>
  )
}

export default FileUpload;