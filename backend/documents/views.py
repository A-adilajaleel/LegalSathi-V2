from rest_framework.decorators import api_view
from rest_framework.response import Response
import os
import fitz
import base64
import re
from groq import Groq
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
from rest_framework import status

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key)


def clean_thinking(text):
    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    text = re.sub(
        r"<think>.*$",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    return text.strip()


def analyze_legal_text(extracted_text):
    prompt = f"""
Analyze the following legal document and explain it in simple language.

Provide:

1. Simple Summary
2. Key Points
3. Important Obligations
4. Important Dates and Amounts
5. Potential Risks

Rules:

- Base the analysis only on information explicitly present in the document.
- Do not invent or assume any legal rights, obligations, dates, amounts, or facts.
- Never calculate dates from durations.
- Never infer an end date unless it is explicitly written.
- Never infer obligations that are not explicitly stated.
- Never add risks based on assumptions.
- Mention only risks that can reasonably be inferred from the document.
- If no explicit risks are present, write "No explicit risks mentioned in the document."
- If information is missing, write "Not specified in the document."
- If a fact is not directly written in the document, do not mention it.
- Do not provide legal advice.
- Use simple and clear English.
- Return only the final analysis.
- Do not include thinking or reasoning.
- Do not include <think> tags.
- Do not describe your analysis process.

Legal Document:

{extracted_text}
"""

    response = client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        reasoning_effort="none",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    analysis = response.choices[0].message.content

    return clean_thinking(analysis)


@api_view(["GET"])
def home(request):
    return Response({
        "message": "LegalSathi API is running"
    })


@api_view(["POST"])
def upload_document(request):
    uploaded_file = request.FILES.get("file")

    if not uploaded_file:
        return Response({
            "error": "No file uploaded"
        }, status=400)

    if uploaded_file.size > 10 * 1024 * 1024:
        return Response({
            "error": "File size must be less than 10 MB."
        }, status=400)

    file_extension = os.path.splitext(uploaded_file.name)[1].lower()

    allowed_extensions = [".pdf", ".jpeg", ".jpg", ".png"]

    if file_extension not in allowed_extensions:
        return Response({
            "error": "Only PDF, JPEG, JPG and PNG files are allowed"
        }, status=400)

    if file_extension == ".pdf":

        pdf_document = fitz.open(
            stream=uploaded_file.read(),
            filetype="pdf"
        )

        extracted_text = ""

        for page in pdf_document:
            extracted_text += page.get_text()

        if not extracted_text.strip():

            extracted_text = ""

            for page in pdf_document:

                pix = page.get_pixmap()

                image_bytes = pix.tobytes("png")

                image_base64 = base64.b64encode(
                    image_bytes
                ).decode("utf-8")

                response = client.chat.completions.create(
                    model="qwen/qwen3.6-27b",
                    reasoning_effort="none",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Extract all text from this legal document image. Return only the extracted text. Do not include explanations, reasoning, or <think> tags."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{image_base64}"
                                    }
                                }
                            ]
                        }
                    ]
                )

                page_text = response.choices[0].message.content

                page_text = clean_thinking(page_text)

                extracted_text += page_text + "\n"

        extracted_text = extracted_text.strip()

        if not extracted_text:
            return Response({
                "error": "No readable text found in the document."
            }, status=400)

        analysis = analyze_legal_text(extracted_text)

        return Response({
            "message": "Document processed successfully",
            "filename": uploaded_file.name,
            "text": extracted_text,
            "analysis": analysis
        })

    if file_extension in [".jpg", ".jpeg", ".png"]:

        image = Image.open(uploaded_file)

        if image.mode != "RGB":
            image = image.convert("RGB")

        image.thumbnail((1024, 1024))

        buffer = BytesIO()

        image.save(
            buffer,
            format="JPEG",
            quality=80
        )

        image_base64 = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")

        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            reasoning_effort="none",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all text from this legal document image. Return only the extracted text. Do not include explanations, reasoning, or <think> tags."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
        )

        extracted_text = response.choices[0].message.content

        extracted_text = clean_thinking(extracted_text)

        if not extracted_text:
            return Response({
                "error": "No readable text found in the document."
            }, status=400)

        analysis = analyze_legal_text(extracted_text)

        return Response({
            "message": "Document processed successfully",
            "filename": uploaded_file.name,
            "text": extracted_text,
            "analysis": analysis
        })


@api_view(["POST"])
def translate_document(request):

    analysis = request.data.get("analysis")
    language = request.data.get("language")

    if not analysis:
        return Response(
            {
                "error": "Analysis is required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if not language:
        return Response(
            {
                "error": "Language is required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    prompt = f"""
You are the official translation engine for LegalSathi AI.

Translate the following English legal document analysis into {language}.

The input can be any type of legal document, including rental agreements,
contracts, notices, applications, agreements, terms and conditions,
or other legal documents.

Your task is ONLY to translate the provided analysis.

STRICT RULES:

- Translate ONLY the provided text.
- Do not add any information.
- Do not remove any information.
- Do not summarize.
- Do not explain.
- Do not provide legal advice.
- Do not change the meaning.
- Do not change any facts.
- Do not invent information.
- Do not assume missing information.
- Do not infer anything that is not present in the input.
- Do not calculate dates.
- Do not create dates from durations.
- Do not create amounts or numbers.
- Do not change names.
- Do not change places.
- Do not change dates.
- Do not change numbers.
- Do not change currency amounts.
- Do not change the identity or role of any person.
- Never swap the roles of people.
- Keep Landlord and Tenant roles correct.
- Preserve all facts and obligations exactly.
- Return ONLY the translation.
- Do not include your reasoning.
- Do not include thinking.
- Do not include <think> tags.
- Do not write "Here is the translation."
- Do not write "Translation:"
- Do not write any introduction or conclusion.

MALAYALAM RULES:

- Use natural, modern Malayalam.
- Use simple Malayalam that an ordinary person can understand.
- Avoid machine-translated Malayalam.
- Avoid highly literary or uncommon Malayalam.
- Translate legal terms naturally.
- Landlord = "വീട്ടുടമ"
- Tenant = "വാടകക്കാരൻ"
- Rental Agreement = "വാടക കരാർ"
- Security Deposit = "സുരക്ഷാ നിക്ഷേപം"
- Monthly Rent = "മാസ വാടക"
- Property = "വസ്തു"
- Termination = "കരാർ അവസാനിപ്പിക്കൽ"
- Written Notice = "എഴുത്തുപരമായ അറിയിപ്പ്"

HINDI RULES:

- Use natural, modern Hindi.
- Use simple Hindi that an ordinary person can understand.
- Avoid overly formal or archaic Hindi.
- Translate legal terms naturally.
- Landlord = "मकान मालिक"
- Tenant = "किरायेदार"
- Rental Agreement = "किराया समझौता"
- Security Deposit = "सुरक्षा जमा"
- Monthly Rent = "मासिक किराया"
- Property = "संपत्ति"
- Termination = "समझौता समाप्त करना"
- Written Notice = "लिखित सूचना"

FACT PRESERVATION:

- Person names must remain unchanged.
- Dates must remain unchanged.
- Numbers must remain unchanged.
- Currency amounts must remain unchanged.
- Places must remain unchanged.
- Roles must remain correct.
- Obligations must remain unchanged.
- Risks must remain unchanged.
- Missing information must not be invented.

FORMATTING:

Preserve:

- Numbering
- Headings
- Bullet points
- Paragraph order
- Markdown formatting
- Names
- Dates
- Numbers
- Currency values

English Legal Analysis:

{analysis}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        reasoning_effort="none",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    translated_text = response.choices[0].message.content

    translated_text = clean_thinking(translated_text)

    return Response({
        "translated_text": translated_text
    })