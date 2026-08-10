from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

import os
import fitz
import base64
import re

from groq import Groq
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO


load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

client = Groq(
    api_key=groq_api_key
)


def clean_ai_response(text):

    if not text:
        return ""

    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    return text.strip()


def analyze_legal_text(extracted_text):

    prompt = f"""
You are LegalSathi AI.

Your job is to explain legal documents in very simple,
easy-to-understand English for ordinary people.

Analyze ONLY the information explicitly present in the
provided legal document.

Do NOT provide legal advice.

Use exactly this structure:

1. Simple Summary

2. Key Points

3. Important Obligations

4. Important Dates and Amounts

5. Potential Risks

IMPORTANT RULES:

- Use ONLY facts explicitly written in the document.
- Do NOT invent any information.
- Do NOT assume any missing information.
- Do NOT calculate dates from durations.
- Do NOT infer an end date from a duration.
- If an end date is not explicitly written, write:
  "Not specified in the document."
- Do NOT infer obligations that are not explicitly written.
- Do NOT invent rights or responsibilities.
- Do NOT invent risks.
- Mention a risk only when it is directly supported by
  something written in the document.
- If no explicit risk is mentioned, write:
  "No explicit risks mentioned in the document."
- Do NOT provide legal advice.
- Keep all names exactly as written.
- Keep all dates exactly as written.
- Keep all numbers and currency amounts exactly as written.
- Keep the roles of people correct.
- Do not confuse Landlord and Tenant.

Use simple everyday English.

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

    return clean_ai_response(analysis)


@api_view(["GET"])
def home(request):

    return Response({
        "message": "LegalSathi API is running"
    })


@api_view(["POST"])
def upload_document(request):

    uploaded_file = request.FILES.get("file")

    if not uploaded_file:
        return Response(
            {
                "error": "No file uploaded"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if uploaded_file.size > 10 * 1024 * 1024:
        return Response(
            {
                "error": "File size must be less than 10 MB."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    file_extension = os.path.splitext(
        uploaded_file.name
    )[1].lower()

    allowed_extensions = [
        ".pdf",
        ".jpeg",
        ".jpg",
        ".png"
    ]

    if file_extension not in allowed_extensions:
        return Response(
            {
                "error": (
                    "Only PDF, JPEG, JPG and PNG "
                    "files are allowed"
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

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
                                    "text": """
Extract ALL visible text from this
legal document image.

Return ONLY the extracted text.

Do not summarize.
Do not explain.
Do not add information.
Do not translate.
Preserve names, dates, numbers,
and amounts exactly as visible.
"""
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url":
                                        f"data:image/png;base64,{image_base64}"
                                    }
                                }
                            ]
                        }
                    ]
                )

                page_text = response.choices[0].message.content

                page_text = clean_ai_response(
                    page_text
                )

                extracted_text += page_text + "\n"

        extracted_text = extracted_text.strip()

        if not extracted_text:
            return Response(
                {
                    "error":
                    "No readable text found in the document."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        analysis = analyze_legal_text(
            extracted_text
        )

        return Response(
            {
                "message":
                "Document processed successfully",
                "filename":
                uploaded_file.name,
                "text":
                extracted_text,
                "analysis":
                analysis
            }
        )

    if file_extension in [
        ".jpg",
        ".jpeg",
        ".png"
    ]:

        image = Image.open(
            uploaded_file
        )

        if image.mode != "RGB":
            image = image.convert("RGB")

        image.thumbnail(
            (1024, 1024)
        )

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
                            "text": """
Extract ALL visible text from this
legal document image.

Return ONLY the extracted text.

Do not summarize.
Do not explain.
Do not add information.
Do not translate.
Preserve names, dates, numbers,
and amounts exactly as visible.
"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url":
                                f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
        )

        extracted_text = response.choices[0].message.content

        extracted_text = clean_ai_response(
            extracted_text
        )

        if not extracted_text:
            return Response(
                {
                    "error":
                    "No readable text found in the document."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        analysis = analyze_legal_text(
            extracted_text
        )

        return Response(
            {
                "message":
                "Document processed successfully",
                "filename":
                uploaded_file.name,
                "text":
                extracted_text,
                "analysis":
                analysis
            }
        )


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

    allowed_languages = [
        "english",
        "malayalam",
        "hindi"
    ]

    if language.lower() not in allowed_languages:
        return Response(
            {
                "error":
                "Supported languages are English, Malayalam and Hindi."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    prompt = f"""
You are the official translation engine for LegalSathi AI.

Translate the following English legal analysis into {language}.

Translate ONLY the provided analysis.

Do NOT add information.
Do NOT remove information.
Do NOT summarize.
Do NOT explain.
Do NOT give legal advice.
Do NOT change the meaning.
Do NOT change any fact.

ROLE AND NAME RULES:

Never change the identity of any person.

Never swap the roles of people.

Landlord means the person who owns or rents out the property.

Tenant means the person who rents the property.

For Malayalam:

Landlord = വീട്ടുടമ
Tenant = വാടകക്കാരൻ
Rental Agreement = വാടക കരാർ
Termination = കരാർ അവസാനിപ്പിക്കൽ
Security Deposit = സുരക്ഷാ നിക്ഷേപം
Monthly Rent = മാസ വാടക
Property = വസ്തു

Do NOT translate Landlord as:
ജമീന്ദാർ
ജന്മി
ഉടമസ്ഥൻ

Use ONLY:
വീട്ടുടമ

Do NOT translate Tenant as:
ഭാടക്കാരൻ
പാട്ടക്കാരൻ
അപ്പാർട്ട്മെന്റ് അധിവാസി
പാട്ടുകാരൻ

Use ONLY:
വാടകക്കാരൻ

For Hindi:

Landlord = मकान मालिक
Tenant = किरायेदार
Rental Agreement = किराया समझौता
Termination = समझौता समाप्त करना
Security Deposit = सुरक्षा जमा
Monthly Rent = मासिक किराया
Property = संपत्ति

FACT PROTECTION:

Never change:

- Names
- Dates
- Numbers
- Currency amounts
- Places
- Roles
- Facts
- Obligations

Arun Kumar must remain Arun Kumar.

Rahul Nair must remain Rahul Nair.

Rs. 12,000 must remain Rs. 12,000.

Rs. 24,000 must remain Rs. 24,000.

Kochi, Kerala must remain Kochi, Kerala.

July 30, 2026 must remain July 30, 2026.

August 1, 2026 must remain August 1, 2026.

11 months must remain 11 months.

30 days must remain 30 days.

Never calculate dates.

Never infer missing dates.

Never infer missing obligations.

Never add facts.

Never add legal rights.

Never add legal advice.

If the original says:

"Not specified in the document."

preserve that meaning.

FORMATTING:

Keep the same:

- Numbering
- Headings
- Bullet points
- Paragraph structure
- Markdown formatting

LANGUAGE QUALITY:

For Malayalam:

Use natural modern Malayalam.

Write as if explaining the document
to an ordinary Malayalam-speaking person.

Do NOT produce machine-translated Malayalam.

Do NOT use highly literary,
archaic or uncommon Malayalam words.

For Hindi:

Use natural modern Hindi.

Do NOT use overly formal or archaic Hindi.

Use simple everyday language.

Return ONLY the translated legal analysis.

Do NOT write:
"Here is the translation."

Do NOT write:
"Translation:"

Legal Analysis:

{analysis}
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

    translated_text = response.choices[0].message.content

    translated_text = clean_ai_response(
        translated_text
    )

    return Response(
        {
            "translated_text":
            translated_text
        }
    )