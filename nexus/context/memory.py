import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal, TypedDict


MEMORY_DIR = Path("memory_data")
MEMORY_FILE = MEMORY_DIR / "memories.json"
MemoryKind = Literal["fact", "preference", "learning"]
MEMORY_KINDS: tuple[MemoryKind, ...] = ("fact", "preference", "learning")


class MemoryItem(TypedDict):
    """一条长期记忆。"""

    id: str
    kind: MemoryKind
    content: str
    created_at: str


@dataclass
class MemoryStore:
    """最小长期记忆存储。

    Session 负责当前会话窗口，MemoryStore 负责跨会话保存的稳定信息。
    第五阶段先让两者在代码上分开，后续再让 Agent 判断什么值得写入长期记忆。
    """

    file_path: Path = MEMORY_FILE
    memories: list[MemoryItem] = field(default_factory=list)

    @classmethod
    def load(cls, file_path: Path = MEMORY_FILE) -> "MemoryStore":
        """从 JSON 文件加载长期记忆。"""
        if not file_path.exists():
            return cls(file_path=file_path)

        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            data = []

        memories = [
            item
            for item in data
            if isinstance(item, dict)
            and isinstance(item.get("id"), str)
            and isinstance(item.get("content"), str)
        ]
        return cls(file_path=file_path, memories=memories)

    def save(self) -> None:
        """保存长期记忆到 JSON 文件。"""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(self.memories, file, ensure_ascii=False, indent=2)

    def add(self, content: str, kind: MemoryKind = "fact") -> MemoryItem:
        """生成不重复的记忆 ID，将新 MemoryItem 加入内存列表并立即持久化。"""
        memory: MemoryItem = {
            "id": self._generate_memory_id(),
            "kind": kind,
            "content": content,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        self.memories.append(memory)
        self.save()
        return memory

    def list_recent(self, limit: int = 10) -> list[MemoryItem]:
        """按存储顺序返回最近 limit 条长期记忆，不修改原记忆列表。"""
        return self.memories[-limit:]

    def get(self, memory_id: str) -> MemoryItem | None:
        """按 ID 获取一条长期记忆。"""
        return next(
            (memory for memory in self.memories if memory["id"] == memory_id),
            None,
        )

    def delete(self, memory_id: str) -> bool:
        """按 ID 删除一条长期记忆。"""
        memory = self.get(memory_id)
        if memory is None:
            return False

        self.memories.remove(memory)
        self.save()
        return True

    def to_messages_text(self, limit: int = 10) -> str:
        """转换成可放入 prompt 的文本。

        普通聊天和 Agent planner 会在调用模型前使用这个转换点注入长期记忆。
        """
        memories = self.list_recent(limit)
        if not memories:
            return "暂无长期记忆。"

        return "\n".join(
            f"- [{memory['kind']}] {memory['content']}" for memory in memories
        )

    def _generate_memory_id(self) -> str:
        """生成一个简单、可读、递增且不会因删除而重复的记忆 ID。"""
        highest_number = 0
        for memory in self.memories:
            prefix, separator, suffix = memory["id"].partition("_")
            if prefix == "mem" and separator and suffix.isdigit():
                highest_number = max(highest_number, int(suffix))

        return f"mem_{highest_number + 1:04d}"
