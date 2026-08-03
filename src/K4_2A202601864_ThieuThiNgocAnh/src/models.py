from dataclasses import dataclass, field


@dataclass
class Document:
    """A text document and the metadata used to retrieve it."""

    id: str
    content: str
    metadata: dict = field(default_factory=dict)
