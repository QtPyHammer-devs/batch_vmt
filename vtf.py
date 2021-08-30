from __future__ import annotations
import enum
import struct
from typing import Any, Dict, List

from PIL import Image


class ImageFormats(enum.Enum):
    ...


class Vtf:
    header: Dict[str, Any]

    def __init__(self, header: VtfHeader, images: List[Image] = []):
        self.header = header
        ...

    @staticmethod
    def from_file(vtf_filename: str) -> Vtf:
        # NOTE: not an actual implementation
        raise NotImplementedError()
        with open(vtf_filename, "rb") as vtf_file:
            signature, *version = struct.unpack("4s2I", vtf_file.read(12))
        assert signature == b"VTF\0"
        header_classes = {(7, 3): VtfHeader_v73}
        try:
            header = header_classes[version]
        except KeyError:
            raise RuntimeError(f"'{vtf_filename}' is a v{version[0]}.{version[1]}, only v7.3 is supported")
        vtf = Vtf(header)
        return vtf


class VtfHeader:
    def __init__(self, *args, **kwargs):
        ...

    @staticmethod
    def from_bytes(self, raw_header: bytes) -> VtfHeader:
        raise NotImplementedError()  # subclass must implement this method!


class VtfHeader_v73(VtfHeader):
    ...
