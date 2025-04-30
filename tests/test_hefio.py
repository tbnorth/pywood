from pathlib import Path
from io import StringIO

from pywood import hefio


def test_hefio_roundtrip():
    path = Path(__file__).with_name("bench.hef")
    assert path.exists()
    with path.open() as stream:
        obj = hefio.HEFFile.from_hef(stream)
    out = StringIO()
    out.write(obj.to_hef())
    assert out.getvalue() == path.read_text()
