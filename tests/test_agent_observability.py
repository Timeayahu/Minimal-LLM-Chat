import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from nexus.agent import handle_agent_message
from nexus.agent.observability import JsonlTraceLogger
from nexus.cli.context_commands import ConfirmCommand
from nexus.context import MemoryStore, Session
from nexus.tools import get_tools


class AgentObservabilityTest(unittest.TestCase):
    def _context(self, temp_dir: str) -> dict:
        """构造一个所有持久化都指向临时目录的隔离 AppContext。"""
        return {
            "session": Session(name="test_session"),
            "memory_store": MemoryStore(file_path=Path(temp_dir) / "memories.json"),
            "commands": {},
            "tools": get_tools(),
            "trace_logger": JsonlTraceLogger(Path(temp_dir) / "traces"),
        }

    def test_tool_run_is_reconstructable_from_event_sequence(self) -> None:
        """验证一次 tool -> final 运行能按事件顺序完整重建。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            context = self._context(temp_dir)
            plans = [
                {"action": "tool", "tool": "echo", "arguments": {"text": "hello"}},
                {"action": "final", "answer": "echo 完成"},
            ]

            with patch("nexus.agent.runtime.decide_agent_step", side_effect=plans):
                handle_agent_message(context, "帮我 echo hello")

            events = context["trace_logger"].read_recent(session_id="test_session")
            self.assertEqual(
                [event["event_type"] for event in events],
                [
                    "run_started",
                    "planner_started",
                    "planner_completed",
                    "tool_requested",
                    "tool_started",
                    "tool_completed",
                    "planner_started",
                    "planner_completed",
                    "final_answer",
                    "run_completed",
                ],
            )
            self.assertEqual(len({event["run_id"] for event in events}), 1)
            self.assertNotIn("traces", context["session"].to_dict())

    def test_legacy_session_trace_field_is_ignored(self) -> None:
        """验证旧会话 JSON 即使包含 traces，仍能加载消息且不恢复双写状态。"""
        session = Session.from_dict(
            {
                "name": "legacy_session",
                "messages": [{"role": "user", "content": "legacy"}],
                "traces": [{"tool_name": "old_tool"}],
            }
        )

        self.assertEqual(session.name, "legacy_session")
        self.assertEqual(session.messages[0]["content"], "legacy")
        self.assertNotIn("traces", session.to_dict())
        self.assertFalse(hasattr(session, "traces"))

    def test_confirmation_continues_the_original_run_id(self) -> None:
        """验证工具暂停并确认后继续原 Run，不会生成第二个 run_id。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            context = self._context(temp_dir)
            first_plan = {
                "action": "tool",
                "tool": "confirm_echo",
                "arguments": {"text": "hello"},
            }
            with patch("nexus.agent.runtime.decide_agent_step", return_value=first_plan):
                handle_agent_message(context, "确认后 echo hello")

            pending = context["session"].pending_tool_call
            self.assertIsNotNone(pending)
            original_run_id = pending["run_id"]

            with patch(
                "nexus.agent.runtime.decide_agent_step",
                return_value={"action": "final", "answer": "已确认完成"},
            ):
                ConfirmCommand().execute(context, [])

            events = context["trace_logger"].read_recent(run_id=original_run_id)
            event_types = [event["event_type"] for event in events]
            self.assertIn("confirmation_requested", event_types)
            self.assertIn("confirmation_received", event_types)
            self.assertEqual(event_types[-1], "run_completed")
            self.assertEqual({event["run_id"] for event in events}, {original_run_id})

    def test_planner_error_ends_with_persisted_run_failed_event(self) -> None:
        """验证 planner 返回结构化错误时，会先记 planner_failed 再记 run_failed。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            context = self._context(temp_dir)
            invalid_plan = {
                "action": "final",
                "answer": "invalid",
                "error": {
                    "kind": "planner_invalid_json",
                    "message": "invalid json",
                    "details": {"raw_answer": "not-json"},
                },
            }

            with patch("nexus.agent.runtime.decide_agent_step", return_value=invalid_plan):
                handle_agent_message(context, "trigger error")

            events = context["trace_logger"].read_recent(session_id="test_session")
            self.assertEqual(events[-2]["event_type"], "planner_failed")
            self.assertEqual(events[-1]["event_type"], "run_failed")
            self.assertEqual(events[-1]["error"]["kind"], "planner_invalid_json")

    def test_unhandled_exception_is_persisted_before_it_escapes(self) -> None:
        """验证未预期异常继续向上抛出前，TraceStore 已保存 run_failed 终态。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            context = self._context(temp_dir)

            with patch(
                "nexus.agent.runtime.decide_agent_step",
                side_effect=RuntimeError("unexpected planner failure"),
            ):
                with self.assertRaises(RuntimeError):
                    handle_agent_message(context, "trigger exception")

            events = context["trace_logger"].read_recent(session_id="test_session")
            self.assertEqual(events[-1]["event_type"], "run_failed")
            self.assertEqual(events[-1]["error"]["kind"], "unhandled_exception")


if __name__ == "__main__":
    unittest.main()
