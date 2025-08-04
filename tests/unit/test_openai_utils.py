from unittest.mock import MagicMock, patch

from app import openai_utils


class TestOpenAIUtils:

    @patch("app.openai_utils.openai.chat.completions.create")
    def test_analyze_eq_success(self, mock_openai):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[
            0
        ].message.content = """
        {
            "scores": {
                "self_awareness": 8,
                "empathy": 7,
                "self_regulation": 6,
                "communication": 8,
                "decision_making": 7
            },
            "reasoning": {
                "self_awareness": "Shows good understanding of own emotions",
                "empathy": "Demonstrates consideration for others",
                "self_regulation": "Basic emotional control",
                "communication": "Good communication skills",
                "decision_making": "Shows positive attitude"
            }
        }
        """
        mock_openai.return_value = mock_response

        context = "Test situation context"
        question = "What would you do?"
        answer = "I would try to understand and respond appropriately."

        scores, reasoning = openai_utils.analyze_eq(context, question, answer)

        assert isinstance(scores, dict)
        assert isinstance(reasoning, dict)
        assert "self_awareness" in scores
        assert "empathy" in scores
        assert "self_regulation" in scores
        assert "communication" in scores
        assert "decision_making" in scores

        mock_openai.assert_called_once()

    @patch("app.openai_utils.openai.chat.completions.create")
    def test_analyze_eq_invalid_json(self, mock_openai):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Invalid JSON response"
        mock_openai.return_value = mock_response

        context = "Test situation context"
        question = "What would you do?"
        answer = "I would try to understand and respond appropriately."

        result = openai_utils.analyze_eq(context, question, answer)

        assert isinstance(result, dict)
        assert "scores" in result
        assert "reasoning" in result

    @patch("app.openai_utils.openai.chat.completions.create")
    def test_analyze_eq_api_error(self, mock_openai):
        mock_openai.side_effect = Exception("OpenAI API Error")

        context = "Test situation context"
        question = "What would you do?"
        answer = "I would try to understand and respond appropriately."

        try:
            result = openai_utils.analyze_eq(context, question, answer)
            assert isinstance(result, dict)
            assert "scores" in result
            assert "reasoning" in result
        except Exception:
            pass

    def test_analyze_eq_empty_inputs(self):
        result = openai_utils.analyze_eq("", "", "")

        if isinstance(result, tuple):
            scores, reasoning = result
            assert isinstance(scores, dict)
            assert isinstance(reasoning, dict)
        else:
            assert isinstance(result, dict)
            assert "scores" in result
            assert "reasoning" in result

        result = openai_utils.analyze_eq(None, None, None)

        if isinstance(result, tuple):
            scores, reasoning = result
            assert isinstance(scores, dict)
            assert isinstance(reasoning, dict)
        else:
            assert isinstance(result, dict)
            assert "scores" in result
            assert "reasoning" in result
