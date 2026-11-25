STEP_TITLES = ("Start exploring", "Practise your skills", "Prepare for feedback")

ROADMAPS: dict[str, tuple[str, str, str]] = {
    "civil_services": (
        "Choose a public issue and summarise it in five sentences.",
        "Compare two sources and note their perspectives.",
        "Discuss your summary with your mentor.",
    ),
    "defense": (
        "Research a service role and its entry requirements.",
        "Map your preparation into a weekly routine.",
        "Review your plan with your mentor.",
    ),
    "teaching": (
        "Choose a topic you enjoy explaining.",
        "Write a short lesson with a practice activity.",
        "Teach it to a friend and ask for feedback.",
    ),
    "technology": (
        "Choose a small problem to solve with code.",
        "Build and test a first version.",
        "Walk your mentor through your project.",
    ),
}

# For fields without their own roadmap yet, and for students still exploring.
EXPLORATION: tuple[str, str, str] = (
    "List three things you enjoy and one career linked to each.",
    "Talk to someone who does one of those jobs, or read about their day.",
    "Write down what surprised you and discuss it with a mentor.",
)


def roadmap_for(field: str | None) -> list[dict[str, str]]:
    steps = ROADMAPS.get(field or "", EXPLORATION)
    return [{"title": t, "text": s} for t, s in zip(STEP_TITLES, steps)]
