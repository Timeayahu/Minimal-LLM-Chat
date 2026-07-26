import json
import tempfile
import unittest
from pathlib import Path

from nexus.context import MemoryStore


class MemoryStoreTest(unittest.TestCase):
    def test_deleted_highest_id_is_not_reused_after_reload(self) -> None:
        """验证删除最大 ID 并重启后，新记忆仍使用更大的编号。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "memories.json"
            store = MemoryStore(file_path=file_path)
            first = store.add("first")
            second = store.add("second")

            self.assertTrue(store.delete(second["id"]))

            reloaded = MemoryStore.load(file_path)
            third = reloaded.add("third")

            self.assertEqual(first["id"], "mem_0001")
            self.assertEqual(second["id"], "mem_0002")
            self.assertEqual(third["id"], "mem_0003")

    def test_legacy_list_file_is_loaded_and_migrated_on_save(self) -> None:
        """验证旧版顶层列表格式可以读取，并在下次写入时迁移到新格式。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "memories.json"
            file_path.write_text(
                json.dumps(
                    [
                        {
                            "id": "mem_0007",
                            "kind": "learning",
                            "content": "legacy",
                            "created_at": "2026-07-25T00:00:00",
                        }
                    ]
                ),
                encoding="utf-8",
            )

            store = MemoryStore.load(file_path)
            new_memory = store.add("new")
            persisted = json.loads(file_path.read_text(encoding="utf-8"))

            self.assertEqual(new_memory["id"], "mem_0008")
            self.assertEqual(persisted["schema_version"], 1)
            self.assertEqual(persisted["next_id"], 9)
            self.assertEqual(len(persisted["memories"]), 2)


if __name__ == "__main__":
    unittest.main()
