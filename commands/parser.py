def parse_command(user_input: str) -> tuple[str, list[str]]:
    """从用户输入中解析命令名和参数。"""
    if not user_input.startswith("/"):
        return "", []

    parts = user_input.split()
    return parts[0], parts[1:]
