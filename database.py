from datetime import datetime

from sqlalchemy import (
    create_engine,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)

from .config import DATABASE_URL


connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True
    )

    username: Mapped[str] = mapped_column(
        String(100)
    )

    age: Mapped[int] = mapped_column(
        Integer
    )

    weight: Mapped[float] = mapped_column(
        Float
    )

    goal: Mapped[str] = mapped_column(
        String(50)
    )

    intensity: Mapped[str] = mapped_column(
        String(20)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    plans: Mapped[list["Plan"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Plan(Base):

    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True
    )

    original_plan: Mapped[str] = mapped_column(
        Text
    )

    updated_plan: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    nutrition_tip: Mapped[str] = mapped_column(
        Text
    )

    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    user: Mapped[User] = relationship(
        back_populates="plans"
    )


def init_db():
    Base.metadata.create_all(
        bind=engine
    )


def save_user(
    user_id: str,
    username: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str
):

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.user_id == user_id)
            .first()
        )

        if user:

            user.username = username
            user.age = age
            user.weight = weight
            user.goal = goal
            user.intensity = intensity

        else:

            user = User(
                user_id=user_id,
                username=username,
                age=age,
                weight=weight,
                goal=goal,
                intensity=intensity
            )

            db.add(user)

        db.commit()
        db.refresh(user)

        return user

    finally:

        db.close()


def save_plan(
    user_pk: int,
    original_plan: str,
    nutrition_tip: str
):

    db = SessionLocal()

    try:

        plan = Plan(
            user_id=user_pk,
            original_plan=original_plan,
            nutrition_tip=nutrition_tip
        )

        db.add(plan)

        db.commit()
        db.refresh(plan)

        return plan

    finally:

        db.close()


def get_user_by_public_id(user_id: str):

    db = SessionLocal()

    try:

        return (
            db.query(User)
            .filter(User.user_id == user_id)
            .first()
        )

    finally:

        db.close()


def get_latest_plan(user_id: str):

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.user_id == user_id)
            .first()
        )

        if not user:
            return None

        return (
            db.query(Plan)
            .filter(Plan.user_id == user.id)
            .order_by(Plan.id.desc())
            .first()
        )

    finally:

        db.close()


def update_plan(
    plan_id: int,
    updated_plan: str,
    feedback: str,
    nutrition_tip: str
):

    db = SessionLocal()

    try:

        plan = (
            db.query(Plan)
            .filter(Plan.id == plan_id)
            .first()
        )

        if not plan:
            return None

        plan.updated_plan = updated_plan
        plan.feedback = feedback
        plan.nutrition_tip = nutrition_tip
        plan.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(plan)

        return plan

    finally:

        db.close()


def get_all_users_with_plans():

    db = SessionLocal()

    try:

        users = (
            db.query(User)
            .order_by(User.created_at.desc())
            .all()
        )

        result = []

        for user in users:

            plans = sorted(
                user.plans,
                key=lambda x: x.id,
                reverse=True
            )

            result.append(
                {
                    "user": user,
                    "plans": plans
                }
            )

        return result

    finally:

        db.close()


def delete_user(user_id: str):

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.user_id == user_id)
            .first()
        )

        if not user:
            return False

        db.delete(user)
        db.commit()

        return True

    finally:

        db.close()