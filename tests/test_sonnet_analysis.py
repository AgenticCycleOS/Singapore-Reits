"""Every S-REIT analysis uses Sonnet 5.5, with local error handling."""
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import claude_analyzer


class SonnetAnalysisTests(unittest.TestCase):
    def test_all_analysis_requests_use_sonnet_and_text_blocks(self):
        client = MagicMock()
        client.messages.create.return_value = SimpleNamespace(
            model="claude-sonnet-5-5", stop_reason="end_turn",
            content=[SimpleNamespace(type="thinking"), SimpleNamespace(type="text", text='{"Retail": "neutral"}')]
        )
        with patch.object(claude_analyzer, "client", client):
            self.assertEqual(claude_analyzer.generate_market_commentary([], {}, {}), '{"Retail": "neutral"}')
            self.assertEqual(claude_analyzer.generate_reit_analysis({"name": "Test", "price": 1, "change_pct": 0}), '{"Retail": "neutral"}')
            self.assertEqual(claude_analyzer.generate_sector_outlook({}, []), {"Retail": "neutral"})
            self.assertEqual(claude_analyzer.generate_portfolio_recommendation([
                {"name": "Test", "price": 1, "change_pct": 0, "dividend_yield": 5}
            ], {}), '{"Retail": "neutral"}')
        self.assertEqual(client.messages.create.call_count, 4)
        for call in client.messages.create.call_args_list:
            self.assertEqual(call.kwargs["model"], "claude-sonnet-5-5")
            self.assertNotIn("fallbacks", call.kwargs)

    def test_refusal_uses_local_fallback_without_requesting_another_model(self):
        client = MagicMock()
        client.messages.create.return_value = SimpleNamespace(
            model="claude-sonnet-5-5", stop_reason="refusal",
            content=[SimpleNamespace(type="text", text="Incomplete")]
        )
        with patch.object(claude_analyzer, "client", client):
            self.assertIsNone(claude_analyzer.generate_reit_analysis({"name": "Test", "price": 1, "change_pct": 0}))
        self.assertEqual(client.messages.create.call_count, 1)
