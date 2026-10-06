from pathlib import Path

from fastapi import (
    APIRouter,
    Form,
    Request
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)

from fastapi.templating import Jinja2Templates


from .database import (
    delete_user,
    get_all_users_with_plans,
    get_latest_plan,
    get_user_by_public_id,
    save_plan,
    save_user,
    update_plan,
)

from .schemas import (
    FeedbackRequest,
    UserInput
)

from .gemini_generator import (
    generate_workout_gemini
)

from .gemini_flash_generator import (
    generate_nutrition_tip_with_flash
)

from .updated_plan import (
    update_workout_plan
)


BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(
    directory=str(
        BASE_DIR / "templates"
    )
)


router = APIRouter()


def error_page(
    request: Request,
    message: str
):

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "message": message
        },
        status_code=400
    )


@router.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@router.post(
    "/generate-workout",
    response_class=HTMLResponse
)
def generate_workout(
    request: Request,

    username: str = Form(...),

    user_id: str = Form(...),

    age: int = Form(...),

    weight: float = Form(...),

    goal: str = Form(...),

    intensity: str = Form(...)
):

    try:

        data = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity
        )

        user = save_user(
            data.user_id,
            data.username,
            data.age,
            data.weight,
            data.goal,
            data.intensity
        )

        workout_plan = generate_workout_gemini(
            data
        )

        nutrition_tip = (
            generate_nutrition_tip_with_flash(
                data.goal,
                data.age
            )
        )

        plan = save_plan(
            user.id,
            workout_plan,
            nutrition_tip
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": data,
                "workout_plan": workout_plan,
                "nutrition_tip": nutrition_tip,
                "plan_id": plan.id,
                "updated": False,
                "message": None
            }
        )

    except ValueError as error:

        return error_page(
            request,
            str(error)
        )

    except Exception as error:

        return error_page(
            request,
            f"Could not generate plan: {error}"
        )


@router.post(
    "/submit-feedback",
    response_class=HTMLResponse
)
def submit_feedback(
    request: Request,

    user_id: str = Form(...),

    feedback: str = Form(...)
):

    try:

        data = FeedbackRequest(
            user_id=user_id,
            feedback=feedback
        )

        user = get_user_by_public_id(
            data.user_id
        )

        plan = get_latest_plan(
            data.user_id
        )

        if not user:

            return error_page(
                request,
                "User not found."
            )

        if not plan:

            return error_page(
                request,
                "Workout plan not found."
            )

        revised_plan = update_workout_plan(
            plan.original_plan,
            data.feedback,
            user.age
        )

        nutrition_tip = (
            generate_nutrition_tip_with_flash(
                user.goal,
                user.age
            )
        )

        update_plan(
            plan.id,
            revised_plan,
            data.feedback,
            nutrition_tip
        )

        user_input = UserInput(
            username=user.username,
            user_id=user.user_id,
            age=user.age,
            weight=user.weight,
            goal=user.goal,
            intensity=user.intensity
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user_input,
                "workout_plan": revised_plan,
                "nutrition_tip": nutrition_tip,
                "plan_id": plan.id,
                "updated": True,
                "message":
                    "Your workout plan has been updated successfully."
            }
        )

    except ValueError as error:

        return error_page(
            request,
            str(error)
        )

    except Exception as error:

        return error_page(
            request,
            f"Could not update plan: {error}"
        )


@router.get(
    "/view-all-users",
    response_class=HTMLResponse
)
def view_all_users(
    request: Request
):

    records = get_all_users_with_plans()

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "records": records
        }
    )


@router.post(
    "/delete-user/{user_id}"
)
def remove_user(
    user_id: str
):

    delete_user(user_id)

    return RedirectResponse(
        url="/view-all-users",
        status_code=303
    )


@router.get("/api/health")
def health():

    return {
        "status": "ok",
        "application": "FitBuddy"
    }


@router.get("/api/users")
def api_users():

    records = get_all_users_with_plans()

    result = []

    for item in records:

        user = item["user"]

        result.append(
            {
                "user_id": user.user_id,
                "username": user.username,
                "age": user.age,
                "weight": user.weight,
                "goal": user.goal,
                "intensity": user.intensity,
                "plans": [
                    {
                        "id": plan.id,
                        "has_updated_plan":
                            bool(plan.updated_plan),
                        "feedback":
                            plan.feedback
                    }
                    for plan in item["plans"]
                ]
            }
        )

    return result