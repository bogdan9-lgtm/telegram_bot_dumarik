from .common import router as common_router
from .fallback import router as fallback_router
from .gpt import router as gpt_router
from .person_talk import router as person_talk_router
from .quiz import router as quiz_router
from .random_fact import router as random_fact_router
from .recommend import router as recommend_router
from .translate import router as translate_router
from .resume import router as resume_router

routers = [
    person_talk_router,
    common_router,
    gpt_router,
    quiz_router,
    random_fact_router,
    translate_router,
    recommend_router,
    resume_router,
    fallback_router,  # завжди останній: ловить усе, що не зловили інші
]
