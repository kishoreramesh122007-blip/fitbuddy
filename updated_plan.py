from google import genai

from .config import (
    GEMINI_API_KEY,
    GEMINI_WORKOUT_MODEL,
    DEMO_MODE,
)


def demo_update(
    original_plan,
    feedback
):

    return f"""
{original_plan}

UPDATED PLAN

User feedback:
{feedback}

The plan has been adjusted according to the requested feedback
while keeping the weekly structure and recovery guidance.

The updated routine should remain comfortable, sustainable
and appropriate for the user's selected intensity.
"""


def update_workout_plan(
    original_plan,
    feedback,
    age
):

    if not GEMINI_API_KEY:

        if DEMO_MODE:
            return demo_update(
                original_plan,
                feedback
            )

        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    prompt = f"""
You are FitBuddy.

Update the following 7-day fitness plan based on
the user's feedback.

USER AGE:
{age}

USER FEEDBACK:
{feedback}

ORIGINAL PLAN:
{original_plan}

RULES:

1. Keep the 7-day structure.
2. Apply the user's feedback where reasonable.
3. Keep the plan safe and sustainable.
4. Include appropriate recovery.
5. Do not recommend unsafe challenges.
6. Do not recommend drugs or performance-enhancing substances.
7. Do not diagnose medical conditions.
8. If the user is under 18, do not provide calorie restriction
   or weight-loss targets.
9. Return the COMPLETE revised plan.

Use simple plain-text headings.
"""

    response = client.models.generate_content(
        model=GEMINI_WORKOUT_MODEL,
        contents=prompt
    )

    result = (response.text or "").strip()

    if not result:
        raise RuntimeError(
            "Gemini returned an empty updated plan."
        )

    return result