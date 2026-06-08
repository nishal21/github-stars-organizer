from dataclasses import dataclass, field


@dataclass
class StarredRepo:
    id: int
    full_name: str
    description: str
    language: str
    topics: list[str]
    html_url: str

    @property
    def owner(self) -> str:
        return self.full_name.split("/")[0]

    @property
    def name(self) -> str:
        return self.full_name.split("/")[1]

    def summary(self) -> str:
        parts = [self.full_name]
        if self.language:
            parts.append(f"[{self.language}]")
        if self.description:
            parts.append(f"- {self.description}")
        if self.topics:
            parts.append(f"({', '.join(self.topics)})")
        return " ".join(parts)


@dataclass
class StarList:
    id: str
    name: str
    description: str = ""


@dataclass
class Assignment:
    repo: str
    list_name: str


@dataclass
class CategorizationResult:
    assignments: list[Assignment] = field(default_factory=list)
    new_lists: list[str] = field(default_factory=list)
