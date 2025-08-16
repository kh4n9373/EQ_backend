from unittest.mock import patch

import pytest


@pytest.mark.integration
def test_analyze_answer_endpoint_happy(client, setup_test_data):
    # Force OpenAI path to deterministic output
    with patch(
        "app.services.analysis_service.OpenAIService.analyze_eq",
        return_value=({"empathy": 8}, {"empathy": "good"}),
    ):
        # endpoint is /api/v1/analysis/analyze
        for sid in [1, 2, 3]:
            resp = client.post(
                "/api/v1/analysis/analyze",
                json={"situation_id": sid, "answer_text": "my answer"},
            )
            if resp.status_code == 200:
                body = resp.json()
                # SuccessResponse wrapper
                assert body["success"] is True
                assert body["data"]["scores"]["empathy"] == 8
                break
        else:
            # If seed ids differ, we still want the endpoint executed at least once
            assert False, "No seeded situation id responded 200"
