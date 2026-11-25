"""The single list of career fields used by the chatbot, mentors and community."""

# key -> long label used in AI prompts (from the intake chatbot prototype)
FIELDS: dict[str, str] = {
    "civil_services": "Civil Services (UPSC, state PSC, administration)",
    "defense": "Defense (NDA, CDS, SSB, police, armed and paramilitary forces)",
    "teaching": "Teaching and Education (school or college teacher, CTET/TET, academia)",
    "technology": "Technology and Engineering (software, AI, engineering)",
    "medical": "Medical and Healthcare",
    "business": "Business, Finance and Commerce",
    "creative": "Creative Fields (design, media, arts, writing)",
    "undecided": "Still exploring - needs more guidance before choosing a field",
}

# key -> short label shown in the app
FIELD_LABELS: dict[str, str] = {
    "civil_services": "Civil Services",
    "defense": "Defence",
    "teaching": "Teaching",
    "technology": "Technology",
    "medical": "Medical",
    "business": "Business",
    "creative": "Creative",
    "undecided": "Still exploring",
}

MENTOR_FIELDS: tuple[str, ...] = tuple(k for k in FIELDS if k != "undecided")
COMMUNITY_FIELDS: tuple[str, ...] = (
    "civil_services", "defense", "teaching", "technology", "undecided",
)


def sql_in(column: str, values: tuple[str, ...]) -> str:
    """Build a CHECK expression such as: field IN ('a', 'b'), from our own constants."""
    quoted = ", ".join(f"'{v}'" for v in values)
    return f"{column} IN ({quoted})"
