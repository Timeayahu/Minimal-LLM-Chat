import os
import unittest

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from nexus.agent.policy import ToolRequest, resolve_tool_request
from nexus.agent.tool_execution import execute_tool
from nexus.tools import ToolError, get_tools


class AgentToolExecutionTest(unittest.TestCase):
    def test_policy_resolves_a_valid_tool_request(self) -> None:
        """验证 Policy 会把合法 Planner 输出解析成可执行 ToolRequest。"""
        resolved = resolve_tool_request(
            {"action": "tool", "tool": "echo", "arguments": {"text": "hello"}},
            get_tools(),
        )

        self.assertIsInstance(resolved, ToolRequest)
        self.assertEqual(resolved.name, "echo")
        self.assertEqual(resolved.arguments, {"text": "hello"})
        self.assertFalse(resolved.requires_confirmation)

    def test_policy_rejects_an_unknown_tool(self) -> None:
        """验证未知工具在进入执行器前就被 Policy 转换成结构化错误。"""
        resolved = resolve_tool_request(
            {"action": "tool", "tool": "missing", "arguments": {}},
            get_tools(),
        )

        self.assertIsInstance(resolved, ToolError)
        self.assertEqual(resolved.kind, "unknown_tool")

    def test_executor_returns_result_observation_and_duration(self) -> None:
        """验证共享执行器会返回工具结果、Planner observation 和执行耗时。"""
        tool = get_tools()["echo"]
        execution = execute_tool(
            ToolRequest(name="echo", arguments={"text": "hello"}, tool=tool)
        )

        self.assertTrue(execution.result.ok)
        self.assertEqual(execution.result_text, "hello")
        self.assertIn("echo({'text': 'hello'}) -> hello", execution.observation)
        self.assertGreaterEqual(execution.duration_ms, 0)


if __name__ == "__main__":
    unittest.main()
