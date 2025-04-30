import json
from typing import Annotated, ClassVar, TextIO

from pydantic import BaseModel, Field

JSON = Annotated[str, Field(description="JSON string")]


class Lath(BaseModel):
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    layer: int
    part: int

    _fields: ClassVar[list[str]] = "x", "y", "z", "vx", "vy", "vz", "layer", "part"

    @staticmethod
    def _intfloat(x):
        return str(int(x) if x == int(x) else x)

    def to_hef(self) -> str:
        return " ".join(map(self._intfloat, (getattr(self, i) for i in self._fields)))

    @classmethod
    def from_hef(cls, text: str):
        text = text.split()
        params = [float(i) for i in text[:6]] + [int(i) for i in text[6:]]
        return cls(**dict(zip(cls._fields, params)))


class HEFFile(BaseModel):
    name: str
    params: dict
    slat: dict
    props: dict
    part_count: int
    part_name: list[str]
    lath: list[Lath]

    def to_hef(self) -> str:
        return "\n".join(
            map(
                str,
                (
                    "Hyperwood Exchange Format",
                    "Version 1",
                    "hyperwood.org",
                    self.name,
                    json.dumps(self.params, separators=(",", ":")),
                    json.dumps(self.slat, separators=(",", ":")),
                    json.dumps(self.props, separators=(",", ":")),
                    self.part_count,
                    "\n".join(self.part_name),
                    "\n".join(i.to_hef() for i in self.lath),
                    "",
                ),
            )
        )

    @classmethod
    def from_hef(cls, stream: TextIO):
        next(stream)  # Format name
        next(stream)  # Format version
        next(stream)  # Format namespace
        return cls(
            name=next(stream).rstrip("\n"),
            params=json.loads(next(stream)),
            slat=json.loads(next(stream)),
            props=json.loads(next(stream)),
            part_count=(part_count := int(next(stream))),
            part_name=list(next(stream).rstrip("\n") for i in range(part_count)),
            lath=[Lath.from_hef(i) for i in stream],
        )
