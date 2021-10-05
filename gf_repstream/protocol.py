#!/usr/bin/env python
from _ctypes import Structure
from ctypes import c_uint64, c_uint16

class RowPerFrame(Structure):
    _pack_ = 1
    _fields_ = [
        ("rpf0",c_bool),  # 1 bit
        ("rpf1",c_bool),  # 1 bit
    ]

    def as_dict(self):
        return dict((f, getattr(self, f)) for f, _ in self._fields_)


class ExposureTime(Structure):
    _pack_ = 1
    _fields_ = [
        ("exptime0", c_uint8),  # 1 bytes
        ("exptime0", c_uint16), # 2 bytes | 3 bytes
    ]
    def as_dict(self):
        return dict((f, getattr(self, f)) for f, _ in self._fields_)


class Timestamp(Structure):
    _pack_ = 1
    _fields_ = [
        ("timestamp0",c_uint32),    # 4 bytes
        ("timestamp1",c_uint8),     # 1 bytes  | 5 bytes
    ]

    def as_dict(self):
        return dict((f, getattr(self, f)) for f, _ in self._fields_)

class RowsPerFramePerQuadrant(Structure):
    _pack_ = 1
    _fields_ = [
        ("rpfpq0",c_bool),  # 1 bit
        ("rpfpq1",c_bool),  # 1 bit
        ("rpfpq2",c_bool),  # 1 bit
        ("rpfpq3",c_bool),  # 1 bit
        ("rpfpq4",c_bool),  # 1 bit
        ("rpfpq5",c_bool),  # 1 bit
        ("rpfpq6",c_bool),  # 1 bit  | 7 bits
    ]

    def as_dict(self):
        return dict((f, getattr(self, f)) for f, _ in self._fields_)

class CorrectionMode(Structure):
    _pack_ = 1
    _fields_ = [
        ("corr_mode0",c_bool),  # 1 bit
        ("corr_mode1",c_bool),  # 1 bit
        ("corr_mode2",c_bool),  # 1 bit  | 3 bits
    ]

    def as_dict(self):
        return dict((f, getattr(self, f)) for f, _ in self._fields_)

class FlagsHeader(Structure):
    _pack_ = 1
    _fields_ = [
        ("do_not_store",c_bool),    # 1 bit
        ("zero",c_bool),            # 1 bit
        ("trigger",c_bool),         # 1 bit
        ("enable",c_bool),          # 1 bit
        ("status0",c_bool),         # 1 bit
        ("status1",c_bool),         # 1 bit
        ("status2",c_bool),         # 1 bit
        ("status3",c_bool),         # 1 bit
        ("status4",c_uint8)         # 8 bits |  16 bits
    ]
    
    def as_dict(self):
        return dict((f, getattr(self, f)) for f, _ in self._fields_)

class GFHeader(Structure):
    _pack_ = 1
    _fields_ = [
        ("protocol_id",c_uint8),        # 1 byte        | 1 byte
        ("row_legth",c_uint8),          # 1 byte        | 2 bytes
        ("rpfpq",RowsPerFramePerQuadrant),  # 7 bits    
        ("swap",c_bool),                # 1 bits        | 3 bytes
        ("N",c_bool),                   # 1 bit
        ("E",c_bool),                   # 1 bit
        ("link",c_bool),                # 1 bit
        ("correction_mode",CorrectionMode),  # 3 bits
        ("rpf", RowPerFrame),                # 2 bits   | 4 bytes
        ("scan_id",c_uint32),           # 4 bytes       | 8 bytes
        ("frame_number",c_uint32),      # 4 bytes       | 12 bytes
        ("flags", FlagsHeader),         # 2 bytes       | 14 bytes
        ("starting_row",c_uint16),      # 2 bytes       | 16 bytes
        ("timestamp",Timestamp),        # 5 bytes       | 21 bytes
        ("exposure_time",ExposureTime), # 3 bytes       | 24 bytes
        ("sync_time",c_uint32),         # 4 bytes       | 28 bytes
        ("scan_time",c_uint32),         # 4 bytes       | 32 bytes (TOTAL)    
    ] # 32 bytes

    def as_dict(self):
        return dict((f, getattr(self, f)) for f, _ in self._fields_)