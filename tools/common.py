"""Shared paths, hashing and MZ parsing."""
import hashlib, json, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'build'
META = ROOT / 'metadata'
PACKED = ROOT / 'assets' / 'dos' / 'UGH.EXE'
TOOLS = Path('C:/tools')

MZ_FIELDS = ('magic', 'last_page_bytes', 'pages', 'reloc_count', 'header_paras', 'min_alloc',
             'max_alloc', 'ss', 'sp', 'checksum', 'ip', 'cs', 'reloc_offset', 'overlay')


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load_json(name):
    return json.loads((META / name).read_text())


class MZ:
    """An MZ executable: header fields, relocation list in file order, load image."""

    def __init__(self, data):
        self.data = data
        self.hdr = dict(zip(MZ_FIELDS, struct.unpack_from('<14H', data)))
        if self.hdr['magic'] != 0x5A4D:
            raise ValueError('not an MZ file')
        h = self.hdr
        self.header_size = h['header_paras'] * 16
        self.file_image_end = h['pages'] * 512 - ((512 - h['last_page_bytes']) % 512)
        self.image = data[self.header_size:self.file_image_end]
        self.tail = data[self.file_image_end:]
        # (offset, segment) pairs exactly as stored
        self.relocs = [struct.unpack_from('<HH', data, h['reloc_offset'] + 4 * i)
                       for i in range(h['reloc_count'])]
        self.sites = [seg * 16 + off for off, seg in self.relocs]
        reloc_end = h['reloc_offset'] + 4 * h['reloc_count']
        self.header_gap = data[28:h['reloc_offset']]      # between fixed header and table
        self.header_pad = data[reloc_end:self.header_size]  # after the table

    def word(self, linear):
        return struct.unpack_from('<H', self.image, linear)[0]

    def identity(self):
        """Everything a rebuilt executable has to reproduce."""
        packed_sites = b''.join(struct.pack('<HH', *r) for r in self.relocs)
        sorted_sites = b''.join(struct.pack('<I', s) for s in sorted(self.sites))
        return {
            'file_size': len(self.data),
            'file_sha256': sha256(self.data),
            'header': {k: self.hdr[k] for k in MZ_FIELDS},
            'header_gap_hex': self.header_gap.hex(),
            'header_pad_all_zero': not any(self.header_pad),
            'image_size': len(self.image),
            'image_sha256': sha256(self.image),
            'tail_size': len(self.tail),
            'reloc_ordered_sha256': sha256(packed_sites),
            'reloc_sorted_sha256': sha256(sorted_sites),
            'reloc_distinct_sites': len(set(self.sites)),
        }
