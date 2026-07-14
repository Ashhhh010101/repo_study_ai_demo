from collections import defaultdict


def detect_stack(scanned_files: list[dict]) -> dict:
    result: dict[str, list[str]] = {
        "languages": [],
        "frameworks": [],
        "package_managers": [],
        "databases": [],
        "infra": [],
        "entrypoints": [],
    }
    bucket = defaultdict(set)

    file_paths = {item["path"] for item in scanned_files}
    for file in scanned_files:
        path = file["path"].lower()
        content = file["content"].lower()
        language = file["language"]
        bucket["languages"].add(language)

        if path.endswith("package.json"):
            bucket["package_managers"].add("npm")
            if "react" in content:
                bucket["frameworks"].add("React")
            if "next" in content:
                bucket["frameworks"].add("Next.js")
            if "vite" in content:
                bucket["frameworks"].add("Vite")
            bucket["frameworks"].add("Node.js")
        if path.endswith("requirements.txt") or path.endswith("pyproject.toml"):
            bucket["package_managers"].add("pip" if path.endswith("requirements.txt") else "poetry/pdm")
            if "fastapi" in content:
                bucket["frameworks"].add("FastAPI")
            if "django" in content:
                bucket["frameworks"].add("Django")
            if "flask" in content:
                bucket["frameworks"].add("Flask")
            if "sqlalchemy" in content:
                bucket["frameworks"].add("SQLAlchemy")
        if path.endswith("dockerfile"):
            bucket["infra"].add("Docker")
        if path.endswith("docker-compose.yml") or path.endswith("docker-compose.yaml"):
            bucket["infra"].add("Docker Compose")
        if "schema.prisma" in path:
            bucket["frameworks"].add("Prisma")
        if "alembic" in path:
            bucket["frameworks"].add("Alembic")
        if "tailwind.config" in path:
            bucket["frameworks"].add("Tailwind CSS")
        if "tsconfig.json" in path:
            bucket["frameworks"].add("TypeScript")
        if "vite.config" in path:
            bucket["frameworks"].add("Vite")
        if "sqlalchemy" in content:
            bucket["databases"].add("SQLAlchemy-managed DB")
        if "postgres" in content:
            bucket["databases"].add("PostgreSQL")
        if "sqlite" in content:
            bucket["databases"].add("SQLite")
        if path.endswith(("main.py", "app.py", "server.ts", "index.tsx", "main.tsx")):
            bucket["entrypoints"].add(file["path"])

    if "readme.md" in {p.lower() for p in file_paths}:
        bucket["entrypoints"].add("README.md")

    for key in result:
        result[key] = sorted(bucket[key])
    return result
