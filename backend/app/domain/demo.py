"""Fixed ids for seeded sample users, so seeding can be repeated safely."""
import uuid

_NAMESPACE = uuid.UUID("6f1f6f0e-6a0b-4c57-9a38-3f7c1f5f9d10")


def seed_id(key: str) -> uuid.UUID:
    return uuid.uuid5(_NAMESPACE, key)


DEMO_USERS: dict[str, uuid.UUID] = {
    "student": seed_id("student"),
    "student_almost": seed_id("student_almost"),
    "student_done": seed_id("student_done"),
    "mentor": seed_id("mentor:civil_services"),
}
