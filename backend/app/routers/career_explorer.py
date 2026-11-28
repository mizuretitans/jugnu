"""Career exploration catalogue and contextual question endpoint."""
from fastapi import APIRouter

from app.deps import StudentDep
from app.schemas.api import CareerExplorerIn, CareerExplorerOut, CareerPathOut
from app.services.career_explorer import answer_question, list_paths
from app.services.intake.llm import LlmDep

router = APIRouter(tags=["career explorer"])


@router.get("/career-explorer/paths", response_model=list[CareerPathOut])
def get_career_paths(_: StudentDep) -> list[dict[str, object]]:
    return list_paths()


@router.post("/career-explorer/messages", response_model=CareerExplorerOut)
def ask_about_path(data: CareerExplorerIn, _: StudentDep, llm: LlmDep) -> CareerExplorerOut:
    reply = answer_question(
        llm,
        data.career_id,
        [message.model_dump() for message in data.history],
        data.text,
    )
    return CareerExplorerOut(reply=reply)
