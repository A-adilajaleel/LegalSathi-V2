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

    language = language.lower().strip()

    if language not in ["malayalam", "hindi"]:
        return Response(
            {"error": "Only Malayalam and Hindi are supported"},
            status=status.HTTP_400_BAD_REQUEST
        )

    prompt = f"""
You are a professional legal document translator.

Translate the following English legal document analysis into {language}.

Your task is ONLY to translate the provided text.

STRICT RULES:

- Translate ONLY the provided source text.
- Do not analyze the document.
- Do not explain the document.
- Do not summarize the document.
- Do not add any information.
- Do not remove any information.
- Do not invent information.
- Do not assume missing information.
- Do not infer information.
- Do not calculate anything.
- Do not create dates, amounts, facts, obligations, or risks.
- Do not provide legal advice.
- Preserve the exact meaning of the source text.
- Preserve all facts and details.
- Preserve all names exactly.
- Preserve all places exactly.
- Preserve all dates exactly.
- Preserve all numbers exactly.
- Preserve all currency amounts exactly.
- Preserve all legal obligations exactly.
- Preserve all risks exactly.
- Preserve the identity and role of every person correctly.
- Never swap the roles of people.
- Never change the relationship between people and their legal roles.
- Preserve the same section numbers.
- Preserve the same headings.
- Preserve the same bullet points.
- Preserve the same paragraph order.
- Preserve markdown formatting.

LANGUAGE RULES:

- Use natural, modern {language}.
- Use simple and easy-to-understand {language}.
- Avoid unnatural machine-translated language.
- Do not translate word-for-word when it produces unnatural sentences.
- Use appropriate and natural legal terminology.
- Keep proper names unchanged.
- Keep places unchanged.
- Keep dates unchanged.
- Keep numbers unchanged.
- Keep currency values unchanged.

ROLE RULE:

Legal roles such as Landlord, Tenant, Owner, Buyer, Seller, Employer, Employee, Applicant, Respondent, Plaintiff, Defendant, or any other role must remain associated with the correct person.

Never swap or confuse legal roles.

OUTPUT RULES:

- Return ONLY the translated text.
- Do not include reasoning.
- Do not include thinking.
- Do not include analysis.
- Do not include <think> tags.
- Do not write "Here is the translation".
- Do not write "Translation:".
- Do not add an introduction.
- Do not add a conclusion.
- Do not add notes or comments.

SOURCE TEXT:

{analysis}
"""

    try:

        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            reasoning_effort="none",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional legal document translator. Return only the translation. Never reveal reasoning or thinking."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        translated_text = response.choices[0].message.content or ""

        translated_text = clean_thinking(translated_text)

        translated_text = re.sub(
            r"(?i)^(here is the translation:|translation:|translated text:)\s*",
            "",
            translated_text
        ).strip()

        if not translated_text:
            return Response(
                {"error": "Translation returned empty text"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            "translated_text": translated_text
        })

    except Exception as e:

        print("Translation Error:", str(e))

        return Response(
            {
                "error": "Translation failed",
                "details": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )