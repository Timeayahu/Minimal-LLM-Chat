def __getattr__(name: str):
    """按需导出 Agent 入口，避免导入 agent.trace 时触发循环导入。"""
    if name == "handle_agent_message":
        from agent.chat import handle_agent_message

        return handle_agent_message

    raise AttributeError(f"module 'agent' has no attribute {name!r}")
