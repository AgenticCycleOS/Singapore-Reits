"""Offline regressions for approved models and complete text responses."""
import unittest
from types import SimpleNamespace

from claude_policy import HAIKU_MODEL, SONNET_MODEL, request_options, response_text


class ModelPolicyTests(unittest.TestCase):
    def test_only_approved_models_can_build_a_request(self):
        for model in ("claude-opus-4-6", "claude-opus-5-5", "claude-sonnet-5",
                      "claude-sonnet-4-6", "claude-haiku-4-5-20251001", ""):
            with self.subTest(model=model), self.assertRaises(ValueError):
                request_options(model)

    def test_sonnet_preserves_nonthinking_mode_without_model_fallback(self):
        options = request_options()
        self.assertEqual(options["model"], SONNET_MODEL)
        self.assertEqual(options["extra_body"]["thinking"], {"type": "between_tools"})
        self.assertEqual(options["extra_body"]["output_config"], {"effort": "low"})
        self.assertNotIn("fallbacks", options["extra_body"])
        self.assertTrue({"temperature", "top_p", "top_k"}.isdisjoint(options))

    def test_complex_analysis_and_haiku_use_explicit_adaptive_thinking(self):
        for model in (HAIKU_MODEL, SONNET_MODEL):
            options = request_options(model, effort="medium", adaptive=True)
            self.assertEqual(options["extra_body"]["thinking"], {"type": "adaptive"})
            self.assertEqual(options["extra_body"]["output_config"], {"effort": "medium"})

    def test_final_text_skips_thinking_and_server_tool_blocks(self):
        response = SimpleNamespace(model=SONNET_MODEL, stop_reason="end_turn", content=[
            SimpleNamespace(type="thinking", text="decoy"),
            SimpleNamespace(type="server_tool_use"),
            SimpleNamespace(type="text", text="First."),
            SimpleNamespace(type="text", text="Second."),
        ])
        self.assertEqual(response_text(response), "First.\nSecond.")

    def test_incomplete_response_never_becomes_a_finished_report(self):
        for reason in ("max_tokens", "refusal", "pause_turn", "tool_use",
                       "model_context_window_exceeded"):
            with self.subTest(reason=reason), self.assertRaises(ValueError):
                response_text(SimpleNamespace(model=SONNET_MODEL, stop_reason=reason,
                    content=[SimpleNamespace(type="text", text="partial")]))

    def test_empty_text_and_unapproved_response_model_are_rejected(self):
        for model, content in ((SONNET_MODEL, []),
                               ("claude-opus-4-6", [SimpleNamespace(type="text", text="answer")])):
            with self.subTest(model=model), self.assertRaises(ValueError):
                response_text(SimpleNamespace(model=model, stop_reason="end_turn", content=content))


if __name__ == "__main__":
    unittest.main()
