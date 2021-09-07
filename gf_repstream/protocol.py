#!/usr/bin/env python
from _ctypes import Structure
from ctypes import c_uint64, c_uint16


class TestMetadata(Structure):
    _pack_ = 1
    _fields_ = [
        ("frame", c_uint64),
        ("htype", c_uint64),
        ("tag", c_uint64),
        ("source", c_uint64),
        ("shape", c_uint64),
        ("type", c_uint64),
        ("endianess", c_uint64),
    ]

    def as_dict(self):
        return dict((f, getattr(self, f)) for f, _ in self._fields_)
