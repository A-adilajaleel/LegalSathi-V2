import React from "react";
import { useNavigate } from "react-router-dom";
import { FaRobot, FaFileUpload, FaBolt, FaShieldAlt } from "react-icons/fa";
import { FaLanguage, FaGlobe } from "react-icons/fa";



const Home = () => {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-[#F7F1E5] text-[#2E2A22] font-sans">

      <nav className="flex justify-between items-center px-10 py-5 border-b border-[#DDD0B3] bg-[#F7F1E5]/90 backdrop-blur sticky top-0 z-20">
        <h1 className="text-2xl font-semibold tracking-tight text-[#2F4A3B] font-serif">
          Legal Sathi
        </h1>

        <ul className="flex gap-10 font-medium text-[#4A4436]">

  <li>
    <a href="#about" className="hover:text-[#2F4A3B] transition-colors">
      About
    </a>
  </li>

  <li>
    <a href="#how-it-works" className="hover:text-[#2F4A3B] transition-colors">
      How It Works
    </a>
  </li>

  <li>
    <a href="#why-choose-us" className="hover:text-[#2F4A3B] transition-colors">
      Why Choose Us
    </a>
  </li>


</ul>
      </nav>

     
      <section  id="about"className="text-center py-28 px-6">
        <span className="inline-block mb-5 h-0.5 w-14 bg-[#B8933F]" />
        <h1
          className="text-5xl md:text-6xl font-semibold mb-6 leading-tight text-[#2E2A22] font-serif"
        >
          Legal Sathi AI
        </h1>

        <p className="text-xl mb-10 text-[#6B6353] max-w-xl mx-auto">
          Understand Legal Documents in Simple Language
        </p>

        <button
          onClick={() => navigate("/file")}
          className="px-8 py-3.5 bg-[#2F4A3B] text-[#F7F1E5] rounded-lg cursor-pointer font-medium tracking-wide hover:bg-[#25392F] transition-colors shadow-sm"
        >
          Get Started
        </button>
      </section>

      <section id= "how-it-works"className="max-w-5xl mx-auto py-20 px-6">
        <h2
          className="text-3xl font-semibold mb-6 text-[#2E2A22] font-serif"
        >
          What is Legal Sathi?
        </h2>

        <p className="mb-4 text-[#4A4436] leading-relaxed">
          LegalSathi is an AI-powered legal document assistant that helps users
          understand complex legal documents in simple language.
        </p>

        <p className="mb-4 text-[#4A4436] leading-relaxed">
          Users can upload PDF or image files.
        </p>

        <p className="text-[#4A4436] leading-relaxed">
          The application extracts the text, analyzes it using AI, and provides
          an easy-to-understand explanation.
        </p>
      </section>

      
      <section id="why-choose-us" className="max-w-5xl mx-auto py-20 px-6">
        <h2
          className="text-3xl font-semibold mb-10 text-[#2E2A22] font-serif"
        >
          How It Works
        </h2>

        <div className="space-y-4">
          {[
            "Upload a PDF or Image",
            "OCR extracts the text",
            "AI analyzes the content",
            "Get a simple explanation",
          ].map((step, i) => (
            <div
              key={i}
              className="flex items-center gap-4 bg-[#EDE2CC] rounded-lg px-5 py-4 border border-[#DDD0B3]"
            >
              <span className="flex items-center justify-center w-8 h-8 rounded-full bg-[#2F4A3B] text-[#F7F1E5] text-sm font-semibold shrink-0">
                {i + 1}
              </span>
              <p className="text-[#2E2A22]">{step}</p>
            </div>
          ))}
        </div>
      </section>

      
      
      <section className="max-w-5xl mx-auto py-20 px-6">
        <h2
          className="text-3xl font-semibold mb-10 text-[#2E2A22] font-serif"
        >
          Why Choose Legal Sathi
        </h2>
 
        <div className="grid md:grid-cols-2 gap-5">
          {[
            [ FaRobot, "AI-Powered Analysis",
                "Uses AI to simplify complex legal documents into clear, easy-to-understand explanations."
            ],
            [FaFileUpload, "Supports PDF & Images",
      "Upload legal documents in PDF or image formats for automatic text extraction and analysis."],
            [FaBolt, "Fast Processing",
      "Get document analysis and translations within seconds through an automated workflow."],
            [FaShieldAlt, "Secure Document Handling",
      "Documents are processed only for analysis and are not permanently stored in the application's database."],
          ].map(([Icon, title, description], i) => (
            <div
              key={i}
              className="flex items-start gap-4 bg-[#EDE2CC] border border-[#DDD0B3] rounded-xl px-6 py-6 hover:shadow-lg hover:border-[#2F4A3B]/40 hover:-translate-y-1 transition-all duration-300"
            >
              <span className="flex items-center justify-center w-12 h-12 rounded-full bg-[#2F4A3B] text-[#F7F1E5] text-xl shrink-0">
                <Icon />
              </span>
              <div>
                <h3 className="text-[#2E2A22] font-semibold text-lg mb-1">{title}</h3>
                <p className="text-[#4A4436] text-sm leading-relaxed">{description}</p>
              </div>
            </div>
          ))}
        </div>
         <div className="mt-8 bg-[#EDE2CC] border border-[#DDD0B3] rounded-xl p-6 flex gap-4">
          <span className="flex items-center justify-center w-12 h-12 rounded-full bg-[#2F4A3B] text-[#F7F1E5] text-xl shrink-0">
            <FaGlobe />
          </span>
          <div>
            <h3 className="text-lg font-semibold text-[#2E2A22] mb-2">
              How Translation Works
            </h3>
            <p className="text-[#4A4436] leading-relaxed">
             Legal Sathi first converts complex legal terminology and technical legal
  language into simple, easy-to-understand English while preserving the
  original meaning of the document. Users who prefer English can read the
  simplified analysis immediately. Users can also switch to Malayalam or
  Hindi with a single click. The translation is generated on demand, so it
  may take a few seconds before the translated analysis is displayed.This allows users to understand
  legal documents in the language they are most familiar with.
            </p>
          </div>
        </div>
      </section>
 

      
     

    
      <footer className="border-t border-[#DDD0B3] py-10 bg-[#EDE2CC]">
        <div className="max-w-5xl mx-auto flex justify-between px-6 text-[#4A4436] flex-wrap gap-4">
          <h3
            className="font-semibold text-[#2F4A3B] font-serif"
          >
            Legal Sathi
          </h3>
          <h3 className="cursor-pointer hover:text-[#2F4A3B] transition-colors">Privacy Policy</h3>
          <h3 className="cursor-pointer hover:text-[#2F4A3B] transition-colors">Contact</h3>
          <h3 className="cursor-pointer hover:text-[#2F4A3B] transition-colors">GitHub</h3>
          <h3 className="cursor-pointer hover:text-[#2F4A3B] transition-colors">LinkedIn</h3>
        </div>
      </footer>
    </div>
  )
}

export default Home