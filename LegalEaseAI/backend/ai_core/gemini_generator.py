import os
from dataclasses import dataclass

from dotenv import load_dotenv

def sanitize_text(text: str) -> str:
    if text is None:
        return ""

    return (
        str(text)
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .strip()
    )


load_dotenv()


@dataclass
class GeminiDocumentGenerator:

    api_key: str | None = None
    model: str | None = None

    def __post_init__(self):

        self.api_key = (
            self.api_key
            or os.getenv("YOUR_API_KEY")
        )

        self.model = (
            self.model
            or os.getenv(
                "GEMINI_MODEL",
                "gemini-2.5-flash"
            )
        )

        self.client = None

        if self.api_key:

            from google import genai

            self.client = genai.Client(
                api_key=self.api_key
            )

    def _build_prompt(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
    ) -> str:

        prompt = f"""
You are LegalEase, an AI-assisted legal document drafting system.

Your job is to create a professional legal document based ONLY
on information supplied by the user.

Do not invent important facts.

DOCUMENT INFORMATION

Document Type:
{document_type}

Parties:
{parties}

Terms and Conditions:
{terms}

Effective Date:
{effective_date}


DOCUMENT REQUIREMENTS

1. Start with a clear document title.

2. Clearly identify the parties.

3. Include the effective date.

4. Organize the document into numbered sections.

5. Include every user-provided term.

6. Do not change the meaning of the supplied terms.

7. Do not invent:
   - names
   - addresses
   - payment amounts
   - dates
   - governing law
   - jurisdictions
   - obligations
   - witnesses
   - notary requirements

8. If important information is missing, use:

[NOT PROVIDED]

9. Use professional and readable legal language.

10. End with appropriate signature blocks.

11. Do not provide explanations outside the document.

12. Do not claim that the document is legally guaranteed,
legally valid, or attorney-approved.

13. Return only the document.

FORMAT

Use Markdown-style headings where useful:

# DOCUMENT TITLE

## 1. SECTION

Text...

## 2. SECTION

Text...

Signature:

____________________________
Name:
Date:

USER DATA ENDS HERE.
"""

        return prompt.strip()

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
    ) -> str:

        if not self.client:

            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Add it to your .env file and restart the backend."
            )

        prompt = self._build_prompt(
            document_type,
            parties,
            terms,
            effective_date,
        )

        from google.genai import types

        response = self.client.models.generate_content(

            model=self.model,

            contents=prompt,

            config=types.GenerateContentConfig(

                temperature=0.2,

                max_output_tokens=12000,
            ),
        )

        text = getattr(
            response,
            "text",
            None
        )

        if not text:

            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return sanitize_text(text)
