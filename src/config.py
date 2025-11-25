from dataclasses import dataclass


@dataclass(frozen=True)
class BoardConfig:
    SIZE: int = 4
