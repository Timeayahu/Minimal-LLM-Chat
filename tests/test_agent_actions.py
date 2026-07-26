import unittest

from nexus.agent.actions import (
    AgentActionParseError,
    parse_agent_action,
)


class AgentActionParsingTest(unittest.TestCase):
    def test_parses_tool_action_from_json(self) -> None:
        action = parse_agent_action(
            '{"action": "tool", "tool": "echo", "arguments": {"text": "hello"}}'
        )

        self.assertEqual(
            action,
            {
                "action": "tool",
                "tool": "echo",
                "arguments": {"text": "hello"},
            },
        )

    def test_parses_final_action_from_mapping(self) -> None:
        action = parse_agent_action({"action": "final", "answer": "完成"})

        self.assertEqual(action, {"action": "final", "answer": "完成"})

    def test_rejects_invalid_json(self) -> None:
        result = parse_agent_action("not-json")

        self.assertIsInstance(result, AgentActionParseError)
        self.assertEqual(result.kind, "planner_invalid_json")

    def test_rejects_unknown_action(self) -> None:
        result = parse_agent_action({"action": "wait"})

        self.assertIsInstance(result, AgentActionParseError)
        self.assertEqual(result.kind, "invalid_agent_action")

    def test_preserves_legacy_planner_error_envelope(self) -> None:
        result = parse_agent_action(
            {
                "action": "final",
                "answer": "invalid",
                "error": {
                    "kind": "planner_invalid_json",
                    "message": "invalid json",
                    "details": {"raw_answer": "not-json"},
                },
            }
        )

        self.assertIsInstance(result, AgentActionParseError)
        self.assertEqual(result.kind, "planner_invalid_json")
        self.assertEqual(result.details, {"raw_answer": "not-json"})

    def test_rejects_missing_final_answer(self) -> None:
        result = parse_agent_action({"action": "final"})

        self.assertIsInstance(result, AgentActionParseError)
        self.assertEqual(result.kind, "invalid_final_answer")

    def test_rejects_invalid_tool_fields(self) -> None:
        invalid_name = parse_agent_action(
            {"action": "tool", "tool": 123, "arguments": {}}
        )
        invalid_arguments = parse_agent_action(
            {"action": "tool", "tool": "echo", "arguments": []}
        )

        self.assertIsInstance(invalid_name, AgentActionParseError)
        self.assertEqual(invalid_name.kind, "invalid_tool_name")
        self.assertIsInstance(invalid_arguments, AgentActionParseError)
        self.assertEqual(invalid_arguments.kind, "invalid_tool_arguments")


if __name__ == "__main__":
    unittest.main()
