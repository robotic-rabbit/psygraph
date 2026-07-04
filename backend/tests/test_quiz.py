import pytest
from httpx import ASGITransport, AsyncClient

from app.config import Settings
from app.db.session import AsyncSessionLocal
from app.dependencies import get_db, get_scoring_service, get_settings
from app.main import app
from app.models.answer import Answer
from app.models.entity import Entity
from app.models.question import Question
from app.services.scoring import ScoringService


@pytest.fixture
async def client(setup_db):
    # FIX 3: Override settings to actually include our test questions in "quick"
    test_settings = Settings(
        DATABASE_URL="sqlite+aiosqlite:///:memory:", QUIZ_VERSIONS={"quick": [1, 2]}
    )
    app.dependency_overrides[get_settings] = lambda: test_settings

    # Populate DB
    async with AsyncSessionLocal() as db:
        db.add_all(
            [
                Question(id=1, pole_left="shy", pole_right="bold"),
                Question(id=2, pole_left="lazy", pole_right="active"),
                Entity(
                    id=999,
                    name="Test Character",
                    entity_type="character",
                    is_aggregated=True,
                ),
                Answer(entity_id=999, question_id=1, value=10.0),
                Answer(entity_id=999, question_id=2, value=20.0),
            ]
        )
        await db.commit()

    # Load matrix
    svc = ScoringService()
    async with AsyncSessionLocal() as db:
        await svc.load_matrix(db)
    app.dependency_overrides[get_scoring_service] = lambda: svc

    async def override_get_db():
        async with AsyncSessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db

    # Use AsyncClient for clean async testing
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_score_matches_correctly(client):
    response = await client.post(
        "/quiz/score",
        json={
            "version": "quick",
            "answers": [
                {"question_id": 1, "value": 10},
                {"question_id": 2, "value": 20},
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert len(body["top_matches"]) == 1
    assert body["top_matches"][0]["name"] == "Test Character"
    assert body["top_matches"][0]["score_percent"] == 100.0
