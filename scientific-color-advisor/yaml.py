class YAMLError(Exception):
    pass


def _parse_scalar(value):
    value = value.strip()
    if not value:
        return ""
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return value


def safe_load(text):
    if text is None:
        return None

    result = {}
    stack = [(0, result)]

    for raw_line in text.splitlines():
      if not raw_line.strip() or raw_line.lstrip().startswith("#"):
          continue

      indent = len(raw_line) - len(raw_line.lstrip(" "))
      line = raw_line.strip()
      if ":" not in line:
          raise YAMLError(f"Invalid YAML line: {raw_line}")

      key, value = line.split(":", 1)
      key = key.strip()
      value = value.strip()

      while stack and indent < stack[-1][0]:
          stack.pop()
      if not stack:
          raise YAMLError("Invalid indentation")

      parent = stack[-1][1]
      if value == "":
          child = {}
          parent[key] = child
          stack.append((indent + 2, child))
      else:
          parent[key] = _parse_scalar(value)

    return result
