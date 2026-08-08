import React,{useState} from "react";
import ReactMarkdown from "react-markdown";
import { FaRegFileAlt, FaFileAlt, FaRobot, FaFileSignature } from "react-icons/fa";
import axios from "axios"



const ResultCard = ({ result }) => {

  const[language,setLanguage] = useState("english")

  const[translatedAnalysis, setTranslatedAnalysis] = useState("")

  const handleTranslate = async (selectedLanguage) => {
  try {
    setLanguage(selectedLanguage);

    if (selectedLanguage === "english") {
      setTranslatedAnalysis("");
      return;
    }

    const response = await axios.post(
      "http://127.0.0.1:8000/api/translate/",
      {
        analysis: result.analysis,
        language: selectedLanguage,
      }
    )

    setTranslatedAnalysis(response.data.translated_text);

  } catch (error) {
    console.log(error);
    alert("Translation failed")
  }
}


  return (
    <div className="mt-10 bg-[#F7F1E5] rounded-3xl shadow-xl p-8 space-y-8 border border-[#DDD0B3] font-sans">
      <div className="flex items-center gap-3 border-b border-[#DDD0B3] pb-4">
        <FaFileAlt className="text-2xl text-[#2F4A3B]" />
        <h2 className="text-3xl font-semibold text-[#2F4A3B] font-serif">
          Document Analysis
        </h2>
      </div>

      <div className="bg-[#EDE2CC] rounded-2xl p-5 border border-[#DDD0B3]">
        <h3 className="flex items-center gap-2 text-xl font-semibold text-[#2F4A3B] mb-2">
          <FaFileSignature />
          File Name
        </h3>
        <p className="inline-block bg-white px-4 py-2 rounded-lg text-[#4A4436] break-all border border-[#DDD0B3]">
         {result.filename}
       </p>
      </div>

      <div className="bg-[#EDE2CC] rounded-2xl p-6 border border-[#DDD0B3]">
        <h3 className="flex items-center gap-2 text-xl font-semibold text-[#2F4A3B] mb-4">
          <FaRobot />
          AI Analysis
        </h3>
             <h4 className="text-sm font-bold text-[#6B6353] mb-3">
  Read Analysis In:
</h4>
         <div className="flex gap-3 mb-6">

       
          <button
          onClick={()=>handleTranslate("english")}
          className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors cursor-pointer ${
            language === "english"
              ? "bg-[#2F4A3B] text-[#F7F1E5] border-[#2F4A3B]"
              : "bg-white text-[#4A4436] border-[#DDD0B3] hover:bg-[#F1E8D4]"
          }`}
          >English</button>
          <button
          onClick={()=>handleTranslate("malayalam")}
          className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors cursor-pointer ${
            language === "malayalam"
              ? "bg-[#2F4A3B] text-[#F7F1E5] border-[#2F4A3B]"
              : "bg-white text-[#4A4436] border-[#DDD0B3] hover:bg-[#F1E8D4]"
          }`}
          >Malayalam</button>
          <button
          onClick={()=>handleTranslate("hindi")}
          className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors cursor-pointer ${
            language === "hindi"
              ? "bg-[#2F4A3B] text-[#F7F1E5] border-[#2F4A3B]"
              : "bg-white text-[#4A4436] border-[#DDD0B3] hover:bg-[#F1E8D4]"
          }`}
          >Hindi</button>
 
        </div>
        <div className="prose prose-lg max-w-none prose-headings:text-[#2E2A22] prose-p:text-[#4A4436] prose-strong:text-[#2E2A22] prose-a:text-[#2F4A3B]">
          <ReactMarkdown>
            {translatedAnalysis || result.analysis}
          </ReactMarkdown>
        </div>
      </div>

      <div className="bg-[#EDE2CC] rounded-2xl p-6 border border-[#DDD0B3]">
        <h3 className="text-xl font-semibold text-[#2E2A22] mb-4">
            <FaRegFileAlt className="text-[#2F4A3B]" />
          Extracted Text
        </h3>
        <div className="max-h-64 overflow-y-auto bg-[#F7F1E5] rounded-xl p-4 border border-[#DDD0B3] text-[#4A4436] whitespace-pre-wrap">
          {result.text}
        </div>
      </div>
    </div>
  )
}

export default ResultCard