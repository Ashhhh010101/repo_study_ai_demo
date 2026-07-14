from collections import defaultdict


def build_folder_map(files: list[dict]) -> dict[str, list[str]]:
    folders: dict[str, list[str]] = defaultdict(list)
    for file in files:
        path = file["path"]
        folder = path.rsplit("/", 1)[0] if "/" in path else "."
        folders[folder].append(path)
    return dict(sorted(folders.items(), key=lambda item: item[0]))


def build_file_tree(files: list[dict]) -> list[dict]:
    tree: dict = {}
    for item in files:
        current = tree
        parts = item["path"].split("/")
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = None

    def serialize(node: dict, prefix: str = "") -> list[dict]:
        items = []
        for name in sorted(node):
            child = node[name]
            current_path = f"{prefix}/{name}".strip("/")
            if child is None:
                items.append({"name": name, "path": current_path, "type": "file"})
            else:
                items.append(
                    {
                        "name": name,
                        "path": current_path,
                        "type": "folder",
                        "children": serialize(child, current_path),
                    }
                )
        return items

    return serialize(tree)
