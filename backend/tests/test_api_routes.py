"""Tests for backend/api routes — Milestone 10.

Uses FastAPI's TestClient (backed by httpx) for synchronous HTTP testing.
These are integration tests: real pipeline, real data, no mocks.

The handler is thin by design — these tests verify that the HTTP layer
correctly wires the request to the service and returns the right shape
and status codes. Business logic is already tested in prior milestones.

Five test groups:

  Group 1 — Health endpoint
    GET /v1/health returns 200 with status and version.

  Group 2 — Valid portfolio (happy path)
    POST /v1/analyze with demo portfolio returns the expected structure.
    Two blind spots, one no-finding, no errors.

  Group 3 — Partial success semantics
    Unknown companies go in errors[], not 4xx.
    Mixed known/unknown returns 200 with partial results.

  Group 4 — Error handling
    Empty portfolio → 422.
    All-unknown portfolio → 422.
    Missing portfolio field → 422 (Pydantic validation).

  Group 5 — Contract compliance
    No engine terminology in the JSON response.
    Response validates against AnalyzeResponseSchema.
    Deterministic: same request → same stable fields.
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from backend.api.app import app
from backend.api.schemas import AnalyzeResponseSchema

TEST_DATE = "2024-12-31"


# ---------------------------------------------------------------------------
# Client fixture
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Shared TestClient for all route tests.

    Module scope so the FastAPI app and PipelineService (which pre-loads
    the asset registry) are created once per test session.
    """
    return TestClient(app)


@pytest.fixture(scope="module")
def demo_response(client: TestClient) -> dict[str, object]:
    """The full response for the standard demo portfolio, called once."""
    response = client.post(
        "/v1/analyze",
        json={"portfolio": ["Apple", "NVIDIA", "Microsoft"], "as_of": TEST_DATE},
    )
    assert response.status_code == 200
    result: dict[str, object] = response.json()
    return result


# ---------------------------------------------------------------------------
# Group 1 — Health endpoint
# ---------------------------------------------------------------------------


class TestHealth:
    def test_health_returns_200(self, client: TestClient) -> None:
        response = client.get("/v1/health")
        assert response.status_code == 200

    def test_health_returns_status_ok(self, client: TestClient) -> None:
        response = client.get("/v1/health")
        assert response.json()["status"] == "ok"

    def test_health_returns_version(self, client: TestClient) -> None:
        response = client.get("/v1/health")
        assert "version" in response.json()


# ---------------------------------------------------------------------------
# Group 2 — Happy path
# ---------------------------------------------------------------------------


class TestAnalyzeHappyPath:
    def test_returns_200(self, client: TestClient) -> None:
        response = client.post(
            "/v1/analyze",
            json={"portfolio": ["Apple", "NVIDIA", "Microsoft"], "as_of": TEST_DATE},
        )
        assert response.status_code == 200

    def test_response_has_metadata(self, demo_response: dict) -> None:  # type: ignore[type-arg]
        assert "metadata" in demo_response
        assert demo_response["metadata"]["hyperion_version"] == "0.1"

    def test_response_has_two_blind_spots(self, demo_response: dict) -> None:  # type: ignore[type-arg]
        assert len(demo_response["blind_spots"]) == 2

    def test_apple_in_blind_spots(self, demo_response: dict) -> None:  # type: ignore[type-arg]
        company_ids = {bs["summary"]["company_id"] for bs in demo_response["blind_spots"]}
        assert "apple-inc" in company_ids

    def test_nvidia_in_blind_spots(self, demo_response: dict) -> None:  # type: ignore[type-arg]
        company_ids = {bs["summary"]["company_id"] for bs in demo_response["blind_spots"]}
        assert "nvidia" in company_ids

    def test_microsoft_in_no_findings(self, demo_response: dict) -> None:  # type: ignore[type-arg]
        ids = {nf["company_id"] for nf in demo_response["no_findings"]}
        assert "microsoft" in ids

    def test_no_errors_for_valid_portfolio(self, demo_response: dict) -> None:  # type: ignore[type-arg]
        assert demo_response["errors"] == []

    def test_portfolio_names_in_response(self, demo_response: dict) -> None:  # type: ignore[type-arg]
        assert "Apple Inc." in demo_response["portfolio"]
        assert "NVIDIA Corporation" in demo_response["portfolio"]
        assert "Microsoft Corporation" in demo_response["portfolio"]

    def test_blind_spot_has_three_sections(self, demo_response: dict) -> None:  # type: ignore[type-arg]
        apple = next(
            bs for bs in demo_response["blind_spots"] if bs["summary"]["company_id"] == "apple-inc"
        )
        assert "summary" in apple
        assert "explanation" in apple
        assert "evidence" in apple

    def test_explanation_has_steps(self, demo_response: dict) -> None:  # type: ignore[type-arg]
        apple = next(
            bs for bs in demo_response["blind_spots"] if bs["summary"]["company_id"] == "apple-inc"
        )
        assert len(apple["explanation"]["steps"]) == 3

    def test_steps_have_traceability_fields(self, demo_response: dict) -> None:  # type: ignore[type-arg]
        apple = next(
            bs for bs in demo_response["blind_spots"] if bs["summary"]["company_id"] == "apple-inc"
        )
        for step in apple["explanation"]["steps"]:
            assert "source_id" in step
            assert "target_id" in step
            assert "relationship_type" in step

    def test_default_as_of_returns_200(self, client: TestClient) -> None:
        """Omitting as_of uses today's date — still returns a valid response."""
        response = client.post(
            "/v1/analyze",
            json={"portfolio": ["Apple"]},
        )
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Group 3 — Partial success semantics
# ---------------------------------------------------------------------------


class TestPartialSuccess:
    def test_unknown_company_goes_to_errors_not_4xx(self, client: TestClient) -> None:
        response = client.post(
            "/v1/analyze",
            json={
                "portfolio": ["Apple", "Hyperion Holdings Ltd"],
                "as_of": TEST_DATE,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["identifier"] == "Hyperion Holdings Ltd"
        assert data["errors"][0]["reason"] == "UNKNOWN_COMPANY"

    def test_partial_success_known_company_still_analyzed(self, client: TestClient) -> None:
        response = client.post(
            "/v1/analyze",
            json={
                "portfolio": ["Apple", "Hyperion Holdings Ltd"],
                "as_of": TEST_DATE,
            },
        )
        assert response.status_code == 200
        data = response.json()
        company_ids = {bs["summary"]["company_id"] for bs in data["blind_spots"]}
        assert "apple-inc" in company_ids


# ---------------------------------------------------------------------------
# Group 4 — Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    def test_empty_portfolio_list_returns_422(self, client: TestClient) -> None:
        response = client.post("/v1/analyze", json={"portfolio": []})
        assert response.status_code == 422

    def test_all_unknown_portfolio_returns_422(self, client: TestClient) -> None:
        """When all identifiers are unknown, no Portfolio can be built → 422."""
        response = client.post(
            "/v1/analyze",
            json={"portfolio": ["UnknownCo A", "UnknownCo B"], "as_of": TEST_DATE},
        )
        assert response.status_code == 422

    def test_missing_portfolio_field_returns_422(self, client: TestClient) -> None:
        """Pydantic validation fails when required field is absent."""
        response = client.post("/v1/analyze", json={})
        assert response.status_code == 422

    def test_404_for_unknown_route(self, client: TestClient) -> None:
        response = client.get("/v1/nonexistent")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Group 5 — Contract compliance
# ---------------------------------------------------------------------------


class TestContractCompliance:
    def test_no_engine_terminology_in_response(
        self,
        demo_response: dict,  # type: ignore[type-arg]
    ) -> None:
        """Engine module names must never appear in the wire format."""
        json_str = json.dumps(demo_response)
        for term in ["janus", "titan", "ReasoningArtifact", "reasoning_chain"]:
            assert term not in json_str.lower(), (
                f"Engine term '{term}' found in HTTP response JSON."
            )

    def test_response_validates_against_schema(
        self,
        demo_response: dict,  # type: ignore[type-arg]
    ) -> None:
        """The HTTP response must parse into AnalyzeResponseSchema without error."""
        parsed = AnalyzeResponseSchema.model_validate(demo_response)
        assert len(parsed.blind_spots) == 2

    def test_categories_are_lowercase(self, demo_response: dict) -> None:  # type: ignore[type-arg]
        for bs in demo_response["blind_spots"]:
            for cat in bs["summary"]["categories"]:
                assert cat == cat.lower()

    def test_severity_field_present(self, demo_response: dict) -> None:  # type: ignore[type-arg]
        for bs in demo_response["blind_spots"]:
            assert bs["summary"]["severity"] in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}

    def test_deterministic_stable_fields(self, client: TestClient) -> None:
        """Same portfolio + same as_of → same stable response fields."""

        def _stable(data: dict) -> dict:  # type: ignore[type-arg]
            """Strip volatile metadata fields before comparison."""
            result = dict(data)
            if "metadata" in result:
                meta = dict(result["metadata"])
                for key in ("processing_time_ms", "request_id", "processed_at"):
                    meta.pop(key, None)
                result["metadata"] = meta
            return result

        r1 = client.post(
            "/v1/analyze",
            json={"portfolio": ["Apple", "NVIDIA"], "as_of": TEST_DATE},
        )
        r2 = client.post(
            "/v1/analyze",
            json={"portfolio": ["Apple", "NVIDIA"], "as_of": TEST_DATE},
        )
        assert r1.status_code == r2.status_code == 200
        assert _stable(r1.json()) == _stable(r2.json())
