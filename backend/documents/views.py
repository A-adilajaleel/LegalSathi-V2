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


def analyze_legal_text(extracted_text):
    prompt = f"""
    Analyze the following legal document and explain it in simple language.

    Provide:
    1. Simple Summary
    2. Key Points
    3. Important Obligations
    4. Important Dates and Amounts
    5. Potential Risks
- Mention only risks that can reasonably be inferred from the document.
- Do not invent hypothetical risks.
- If none are present, write "No explicit risks mentioned in the document."


    Important Rules:
- Base the analysis only on information explicitly present in the document.
- Do not invent or assume any legal rights, obligations, dates, amounts, or facts.
- Never calculate dates from durations.
- Never infer an end date unless it is explicitly written.
- Never infer obligations that are not explicitly stated.
- Never add risks that are based on assumptions.
- If information is missing, write "Not specified in the document."
- If a fact is not directly written in the document, do not mention it.
- Do not provide legal advice.

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

    analysis = re.sub(
        r"<think>.*?</think>",
        "",
        analysis,
        flags=re.DOTALL
    ).strip()

    return analysis


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
                image_base64 = base64.b64encode(image_bytes).decode("utf-8")

                response = client.chat.completions.create(
                    model="qwen/qwen3.6-27b",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Extract all text from this legal document image. Return only the extracted text."
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

                page_text = re.sub(
                    r"<think>.*?</think>",
                    "",
                    page_text,
                    flags=re.DOTALL
                ).strip()

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
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all text from this legal document image. Return only the extracted text."
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

        extracted_text = re.sub(
            r"<think>.*?</think>",
            "",
            extracted_text,
            flags=re.DOTALL
        ).strip()


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
@api_view(['POST'])
def translate_document(request):
    analysis = request.data.get("analysis")
    language = request.data.get("language")

    if not analysis:
        return Response(
            {
                "error":"Analysis is required"
            },
            status = status.HTTP_400_BAD_REQUEST
        )
    if not language:
        return Response(
            {
                "error":"Language is required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    prompt = f"""
       You are the official translation engine for LegalSathi AI.

Translate the following English legal document analysis into {language}.

The input may be any type of legal document, including rental
agreements, contracts, notices, applications, agreements,
terms and conditions, or other legal documents.

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
- Keep Landlord and Tenant roles correct whenever they appear.
- Preserve all facts and obligations exactly.

LANGUAGE RULES:

For Malayalam:
- Use natural, modern Malayalam.
- Use simple Malayalam that an ordinary person can understand.
- Avoid machine-translated Malayalam.
- Avoid highly literary or uncommon Malayalam.
- Translate legal terms naturally.
- Do not use incorrect Malayalam alternatives for legal roles.
- Landlord should be translated as "വീട്ടുടമ".
- Tenant should be translated as "വാടകക്കാരൻ".
- Rental Agreement should be translated as "വാടക കരാർ".
- Security Deposit should be translated as "സുരക്ഷാ നിക്ഷേപം".
- Monthly Rent should be translated as "മാസ വാടക".
- Property should be translated as "വസ്തു".
- Termination should be translated as "കരാർ അവസാനിപ്പിക്കൽ".
- Written Notice should be translated as "എഴുത്തുപരമായ അറിയിപ്പ്".

For Hindi:
- Use natural, modern Hindi.
- Use simple Hindi that an ordinary person can understand.
- Avoid overly formal or archaic Hindi.
- Translate legal terms naturally.
- Landlord should be translated as "मकान मालिक".
- Tenant should be translated as "किरायेदार".
- Rental Agreement should be translated as "किराया समझौता".
- Security Deposit should be translated as "सुरक्षा जमा".
- Monthly Rent should be translated as "मासिक किराया".
- Property should be translated as "संपत्ति".
- Termination should be translated as "समझौता समाप्त करना".
- Written Notice should be translated as "लिखित सूचना".

FACT PRESERVATION:

If the input contains:

- Person names → keep them unchanged.
- Dates → keep the same date and year.
- Numbers → keep the same numbers.
- Currency amounts → keep the same amounts.
- Places → keep the same places.
- Roles → preserve the same roles.
- Obligations → preserve the same obligations.
- Risks → preserve the same risks.
- Headings → preserve their meaning.
- Missing information → do not invent it.
FORMATTING:

Preserve the original structure.

Keep:

- Numbering
- Headings
- Bullet points
- Paragraph order
- Markdown formatting
- Important values
- Names
- Dates
- Numbers

Do not add introductory text.

Do not write:

"Here is the translation."

Do not write:

"Translation:"

Do not write:

"Here is the translated text."
Return ONLY the translated legal analysis.



        

        Legal Analysis:{analysis}
        """
    response = client.chat.completions.create(
        model = "qwen/qwen3.6-27b",
       
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    translated_text = response.choices[0].message.content

    translated_text = re.sub(
        r"<think>.*?</think>",
        "",
        translated_text,
        flags=re.DOTALL | re.IGNORECASE
    ).strip()
    

    return Response({
        "translated_text":translated_text
    })
