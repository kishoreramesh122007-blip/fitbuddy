from google import genai

from .config import (
    GEMINI_API_KEY,
    GEMINI_TIP_MODEL,
    DEMO_MODE,
)


def generate_nutrition_tip_with_flash(
    goal: str,
    age: int
):

    if not GEMINI_API_KEY:

        if DEMO_MODE:

            tips = {
                "weight loss":
                    "Choose balanced meals with vegetables or fruit and a protein source. Avoid extreme dieting and focus on regular meals, hydration and sleep.",

                "muscle gain":
                    "Include a protein-rich food with regular meals and prioritize enough food, hydration and sleep.",

                "general wellness":
                    "Aim for varied foods, regular meals, enough hydration and consistent sleep.",

                "flexibility":
                    "Support recovery with balanced meals, hydration and regular sleep."
            }

            return tips.get(
                goal,
                "Choose varied foods, stay hydrated and prioritize regular sleep."
            )

        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    prompt = f"""
Give one short nutrition or recovery tip.

Fitness goal:
{goal}

Age:
{age}

Rules:
- Give practical general wellness advice.
- Do not prescribe medical treatment.
- Do not recommend supplements or drugs.
- If the user is under 18, focus on balanced nutrition,
  hydration, recovery and healthy routines.
- Keep the answer to 2-4 simple sentences.
"""

    response = client.models.generate_content(
        model=GEMINI_TIP_MODEL,
        contents=prompt
    )

    result = (response.text or "").strip()

    if not result:
        raise RuntimeError(
            "Gemini returned an empty nutrition tip."
        )

    return result