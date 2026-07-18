import json
import tempfile
import unittest
from pathlib import Path

from nexus.agent.observability import JsonlTraceLogger, create_trace_event


class JsonlTraceLoggerTest(unittest.TestCase):
    def test_record_immediately_persists_and_can_filter_events(self) -> None:
        """验证 record 返回前文件已写入，且可按 session_id/run_id 筛选。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            trace_dir = Path(temp_dir)
            logger = JsonlTraceLogger(trace_dir)
            first = create_trace_event(
                event_type="run_started",
                session_id="session_a",
                run_id="run_a",
                status="running",
            )
            second = create_trace_event(
                event_type="run_completed",
                session_id="session_b",
                run_id="run_b",
                status="success",
            )

            logger.record(first)
            trace_files = list(trace_dir.glob("trace_*.jsonl"))
            self.assertEqual(len(trace_files), 1)
            self.assertEqual(
                json.loads(trace_files[0].read_text(encoding="utf-8").strip()),
                first,
            )

            logger.record(second)
            self.assertEqual(logger.read_recent(session_id="session_a"), [first])
            self.assertEqual(logger.read_recent(run_id="run_b"), [second])

    def test_sensitive_fields_are_redacted_before_persisting(self) -> None:
        """验证嵌套参数里的 API Key 和 token 在构造事件时已被脱敏。"""
        event = create_trace_event(
            event_type="tool_requested",
            session_id="session_a",
            run_id="run_a",
            data={
                "arguments": {
                    "api_key": "should-not-be-saved",
                    "nested": {"access_token": "should-not-be-saved"},
                    "text": "safe",
                }
            },
        )

        arguments = event["data"]["arguments"]
        self.assertEqual(arguments["api_key"], "[REDACTED]")
        self.assertEqual(arguments["nested"]["access_token"], "[REDACTED]")
        self.assertEqual(arguments["text"], "safe")

    def test_incomplete_json_line_does_not_hide_previous_events(self) -> None:
        """模拟进程崩溃留下不完整末行，验证之前的有效事件仍可读取。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            trace_dir = Path(temp_dir)
            logger = JsonlTraceLogger(trace_dir)
            event = create_trace_event(
                event_type="run_started",
                session_id="session_a",
                run_id="run_a",
            )
            logger.record(event)
            trace_file = next(trace_dir.glob("trace_*.jsonl"))
            with trace_file.open("a", encoding="utf-8") as file:
                file.write('{"event_type": "broken"')

            self.assertEqual(logger.read_recent(run_id="run_a"), [event])


if __name__ == "__main__":
    unittest.main()
