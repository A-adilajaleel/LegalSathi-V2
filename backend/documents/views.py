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
     You are an expert legal translator for LegalSathi AI.

Translate the following legal analysis into {language}.

IMPORTANT INSTRUCTIONS:

- Translate ONLY the provided legal analysis.
- Preserve the exact meaning of the original text.
- Do not add, remove, summarize, or invent any information.
- Keep the same headings, numbering, bullet points, and markdown formatting.
- Translate every sentence completely.
- Use natural, fluent, simple {language} that an ordinary person can easily understand.
- Avoid literal or awkward word-for-word translation.
- Do not mix English with {language} unless the English term is a proper noun or is necessary for clarity.

ROLE AND NAME RULES:
- Never change the identity of any person.
- Never confuse the Landlord and Tenant.
- Translate role names naturally into the target language.
- In Malayalam, translate "Landlord" as "വീട്ടുടമ".
- In Malayalam, translate "Tenant" as "വാടകക്കാരൻ".
- In Malayalam, translate "Rental Agreement" as "വാടക കരാർ".
- In Malayalam, translate "Termination" as "കരാർ അവസാനിപ്പിക്കൽ".
- In Hindi, translate "Landlord" as "मकान मालिक".
- In Hindi, translate "Tenant" as "किरायेदार".
- In Hindi, translate "Rental Agreement" as "किराया समझौता".
- In Hindi, translate "Termination" as "समझौता समाप्त करना".
- Do not use uncommon or archaic words when a simple common word is available.

FACT AND NUMBER RULES:
- Never change names.
- Never change dates.
- Never change numbers.
- Never change currency amounts.
- Keep places unchanged.
- Never calculate or infer missing dates.
- Never infer missing facts or obligations.
- If the original says "Not specified in the document", preserve that meaning.
- Do not provide additional legal advice or commentary.

LANGUAGE QUALITY:
- Malayalam must sound like natural everyday Malayalam, not machine-translated Malayalam.
- Hindi must sound like natural everyday Hindi, not machine-translated Hindi.
- Keep legal meaning accurate while making the language easy to understand.

Return ONLY the translated legal analysis.


        

        Legal Analysis:{analysis}
        """
    response = client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
       
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
    flags=re.DOTALL
).strip()
    

    return Response({
        "translated_text":translated_text
    })
