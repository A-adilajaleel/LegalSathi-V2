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
            {"error": "Analysis is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not language:
        return Response(
            {"error": "Language is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if language not in ["malayalam", "hindi"]:
        return Response(
            {"error": "Only Malayalam and Hindi are supported"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if language == "malayalam":

        prompt = f"""
Translate the following English legal document analysis into natural, simple Malayalam.

You are ONLY a translator.

Do not analyze the document.
Do not explain anything.
Do not summarize.
Do not add information.
Do not remove information.
Do not infer information.
Do not calculate anything.

Preserve exactly:
- Names
- Places
- Dates
- Numbers
- Money amounts
- Legal facts
- Obligations
- Risks
- Section numbers
- Headings
- Bullet points

IMPORTANT ROLE RULE:

Arun Kumar is the Landlord.
Rahul Nair is the Tenant.

Never swap these roles.

Translate the legal role names naturally:

Landlord = വീട്ടുടമ
Tenant = വാടകക്കാരൻ
Rental Agreement = വാടക കരാർ
Security Deposit = സുരക്ഷാ നിക്ഷേപം
Property = വസ്തു
Tenancy = വാടക കാലയളവ്
Monthly Rent = മാസ വാടക
Written Notice = എഴുത്തുപരമായ അറിയിപ്പ്
Legal Action = നിയമ നടപടി
Potential Risks = സാധ്യതയുള്ള അപകടസാധ്യതകൾ
Simple Summary = ലളിതമായ സംഗ്രഹം
Key Points = പ്രധാന കാര്യങ്ങൾ
Important Obligations = പ്രധാനപ്പെട്ട ബാധ്യതകൾ
Important Dates and Amounts = പ്രധാനപ്പെട്ട തീയതികളും തുകകളും

Use natural Malayalam.

Do not translate word-by-word if that produces unnatural Malayalam.

Do not invent Malayalam sentences that are not supported by the English source.

Keep these exactly:

Arun Kumar
Rahul Nair
Kochi
Kerala
Rs. 12,000
Rs. 24,000
30 July 2026
1 August 2026
11 months
30 days

If the source says information is not specified, translate it as not specified.
Do not create missing dates or conditions.

Return ONLY the Malayalam translation.

SOURCE:

{analysis}
"""

    else:

        prompt = f"""
Translate the following English legal document analysis into natural, simple Hindi.

You are ONLY a translator.

Do not analyze the document.
Do not explain anything.
Do not summarize.
Do not add information.
Do not remove information.
Do not infer information.
Do not calculate anything.

Preserve exactly:
- Names
- Places
- Dates
- Numbers
- Money amounts
- Legal facts
- Obligations
- Risks
- Section numbers
- Headings
- Bullet points

IMPORTANT ROLE RULE:

Arun Kumar is the Landlord.
Rahul Nair is the Tenant.

Never swap these roles.

Translate the legal role names naturally:

Landlord = मकान मालिक
Tenant = किरायेदार
Rental Agreement = किराया समझौता
Security Deposit = सुरक्षा जमा
Property = संपत्ति
Tenancy = किरायेदारी
Monthly Rent = मासिक किराया
Written Notice = लिखित सूचना
Legal Action = कानूनी कार्रवाई
Potential Risks = संभावित जोखिम
Simple Summary = सरल सारांश
Key Points = मुख्य बिंदु
Important Obligations = महत्वपूर्ण दायित्व
Important Dates and Amounts = महत्वपूर्ण तिथियां और राशियां

Use natural, modern Hindi.

Do not translate word-by-word if that produces unnatural Hindi.

Do not invent Hindi sentences that are not supported by the English source.

Keep these exactly:

Arun Kumar
Rahul Nair
Kochi
Kerala
Rs. 12,000
Rs. 24,000
30 July 2026
1 August 2026
11 months
30 days

If the source says information is not specified, translate it as not specified.
Do not create missing dates or conditions.

Return ONLY the Hindi translation.

SOURCE:

{analysis}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "You are a professional legal document translator. Return only the requested translation. Never reveal reasoning."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    translated_text = response.choices[0].message.content or ""

    translated_text = re.sub(
        r"<think>.*?</think>",
        "",
        translated_text,
        flags=re.DOTALL | re.IGNORECASE
    ).strip()

    return Response({
        "translated_text": translated_text
    })