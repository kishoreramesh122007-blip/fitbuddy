from google import genai

from .config import (
    GEMINI_API_KEY,
    GEMINI_WORKOUT_MODEL,
    DEMO_MODE,
)


def demo_workout(user):

    return f"""
FITBUDDY 7-DAY FITNESS PLAN

Name: {user.username}
Age: {user.age}
Weight: {user.weight} kg
Goal: {user.goal.title()}
Intensity: {user.intensity.title()}


DAY 1 - FULL BODY

Warm-up:
5-10 minutes of comfortable movement.

Main workout:
- Bodyweight squats
- Wall or incline push-ups
- Glute bridges
- Bird-dog exercise

Cooldown:
Gentle stretching and relaxed walking.


DAY 2 - CARDIO & MOBILITY

Warm-up:
5 minutes easy movement.

Main workout:
Comfortable walking or cycling followed by mobility exercises.

Cooldown:
Gentle stretching.


DAY 3 - UPPER BODY & CORE

Warm-up:
5-10 minutes.

Main workout:
- Wall/incline push-ups
- Resistance-band rows if available
- Dead bugs
- Comfortable core exercises

Cooldown:
Gentle stretching.


DAY 4 - RECOVERY

Take an easy recovery day.

Optional:
- Easy walking
- Gentle mobility
- Relaxation


DAY 5 - LOWER BODY

Warm-up:
5-10 minutes.

Main workout:
- Bodyweight squats
- Step-ups
- Glute bridges
- Calf raises

Cooldown:
Gentle stretching.


DAY 6 - FULL BODY

Warm-up:
5-10 minutes.

Main workout:
A comfortable circuit using:
- Squats
- Incline push-ups
- Glute bridges
- Marching

Cooldown:
Easy walking and stretching.


DAY 7 - REST & RECOVERY

Focus on:
- Rest
- Hydration
- Sleep
- Gentle movement if comfortable


SAFETY NOTE

Start comfortably and focus on proper technique.
Stop if you feel pain, dizziness, or feel unwell.
This application provides general wellness information and is not medical advice.
"""


def generate_workout_gemini(user):

    if not GEMINI_API_KEY:

        if DEMO_MODE:
            return demo_workout(user)

        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    if user.age < 18:

        age_instruction = """
The user is under 18.
Focus only on age-appropriate general wellness,
healthy movement, recovery and enjoyment.
Do not provide calorie restriction,
weight-loss targets, supplements or extreme exercise.
"""

    else:

        age_instruction = """
Keep recommendations sustainable,
moderate and safety-conscious.
"""

    prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

Create a personalized 7-day fitness plan.

USER INFORMATION:

Name: {user.username}
Age: {user.age}
Weight: {user.weight} kg
Fitness Goal: {user.goal}
Workout Intensity: {user.intensity}

REQUIREMENTS:

1. Create exactly Day 1 through Day 7.
2. Include warm-up.
3. Include main workout.
4. Include cooldown/recovery.
5. Give simple exercise instructions.
6. Include appropriate rest/recovery.
7. Keep the plan realistic.
8. Do not diagnose medical conditions.
9. Do not recommend unsafe challenges.
10. Do not recommend drugs or performance-enhancing substances.
11. {age_instruction}

Use simple headings and plain text.
Do not use a table.

Finish with a short safety note.
"""

    response = client.models.generate_content(
        model=GEMINI_WORKOUT_MODEL,
        contents=prompt
    )

    result = (response.text or "").strip()

    if not result:

        raise RuntimeError(
            "Gemini returned an empty workout plan."
        )

    return result