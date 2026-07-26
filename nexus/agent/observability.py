"""独立的 Agent Trace 持久化边界。"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol, TypedDict
from uuid import uuid4


class TraceEvent(TypedDict):
    """Agent Run 中一条可持久化的结构化观测事件。"""

    event_id: str
    event_type: str
    created_at: str
    session_id: str
    run_id: str
    status: str
    step: int | None
    duration_ms: float | None
    data: dict[str, Any]
    error: dict[str, Any] | None


TRACES_DIR = Path("traces")
SENSITIVE_KEY_PARTS = ("api_key", "authorization", "password", "secret", "token")


class TraceLogger(Protocol): # 声明约束类，满足该类写法的都可以被认为是这个类，tracelogger仅作为声明，供后续扩展用，不关心具体实现
    """Agent Runtime 依赖的最小 TraceLogger 接口，屏蔽具体存储方式。"""

    def record(self, event: TraceEvent) -> None:
        """接收已构造的 TraceEvent，并在返回前完成该事件的存储。"""

    def read_recent(
        self,
        *,
        session_id: str | None = None,
        run_id: str | None = None,
        limit: int = 30,
    ) -> list[TraceEvent]:
        """按可选 Session/Run 条件筛选，返回时间最接近的 limit 条事件。"""


class JsonlTraceLogger:
    """以 JSON Lines 追加方式实时保存 Trace 事件。"""

    def __init__(self, directory: Path = TRACES_DIR) -> None:
        """设置 JSONL 文件目录；此时不创建目录，首次 record 时才创建。"""
        self.directory = directory

    def record(self, event: TraceEvent) -> None:
        """
        根据事件日期选择文件，并把该事件追加成一行 JSON。

        函数每次都打开、写入并关闭文件，因此不需要等待
        Session.save()；进程中途退出时，之前完成的行仍保留。
        """
        self.directory.mkdir(parents=True, exist_ok=True)
        file_path = self._file_path_for_event(event)
        with file_path.open("a", encoding="utf-8") as file:
            json.dump(event, file, ensure_ascii=False)
            file.write("\n")

    def read_recent(
        self,
        *,
        session_id: str | None = None,
        run_id: str | None = None,
        limit: int = 30,
    ) -> list[TraceEvent]:
        """
        跨所有按日分割的 JSONL 文件读取、筛选并排序运行事件。

        session_id 和 run_id 都是可选条件；传入时只保留匹配事件。
        limit <= 0 或目录不存在时直接返回空列表。
        """
        if limit <= 0 or not self.directory.exists():
            return []

        matched: list[TraceEvent] = []
        for file_path in sorted(self.directory.glob("trace_*.jsonl"), reverse=True):
            for event in self._read_file(file_path):
                if session_id is not None and event.get("session_id") != session_id:
                    continue
                if run_id is not None and event.get("run_id") != run_id:
                    continue
                matched.append(event)

        matched.sort(key=lambda event: event.get("created_at", ""))
        return matched[-limit:]

    def _file_path_for_event(self, event: TraceEvent) -> Path:
        """把事件 created_at 的日期转成 `trace_YYYYMMDD.jsonl` 文件路径。"""
        created_at = event.get("created_at", "")
        date_text = created_at[:10].replace("-", "")
        if len(date_text) != 8 or not date_text.isdigit():
            date_text = datetime.now().strftime("%Y%m%d")
        return self.directory / f"trace_{date_text}.jsonl"

    @staticmethod
    def _read_file(file_path: Path) -> list[TraceEvent]:
        """逐行解析一个 JSONL 文件，忽略无法解析的损坏行并返回有效事件。"""
        events: list[TraceEvent] = []
        with file_path.open("r", encoding="utf-8") as file:
            for line in file:
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    # 忽略崩溃时可能留下的最后一行不完整记录。
                    continue
                if isinstance(data, dict):
                    events.append(data)  # type: ignore[arg-type]
        return events


def new_run_id() -> str:
    """生成 UUID 构成的唯一 run_id，用于关联一次用户请求的全部事件。"""
    return f"run_{uuid4().hex}"


def create_trace_event(
    *,
    event_type: str,
    session_id: str,
    run_id: str,
    status: str = "info",
    step: int | None = None,
    duration_ms: float | None = None,
    data: dict[str, Any] | None = None,
    error: dict[str, Any] | None = None,
) -> TraceEvent:
    """
    为业务事件补齐 ID、时间、关联字段和可选耗时，返回 TraceEvent。

    data 和 error 在返回前会递归脱敏。本函数只负责构造数据，
    不写文件；真正持久化由 TraceLogger.record() 完成。
    """
    return {
        "event_id": f"evt_{uuid4().hex}",
        "event_type": event_type,
        "created_at": datetime.now().isoformat(timespec="milliseconds"),
        "session_id": session_id,
        "run_id": run_id,
        "status": status,
        "step": step,
        "duration_ms": duration_ms,
        "data": _sanitize(data or {}),
        "error": _sanitize(error) if error is not None else None,
    }


def _sanitize(value: Any) -> Any:
    """递归复制 dict/list，将名称含常见敏感关键字的字段值替换为 `[REDACTED]`。"""
    if isinstance(value, dict):
        sanitized = {}
        for key, item in value.items():
            key_text = str(key)
            if any(part in key_text.lower() for part in SENSITIVE_KEY_PARTS):
                sanitized[key_text] = "[REDACTED]"
            else:
                sanitized[key_text] = _sanitize(item)
        return sanitized
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    return value
