import gzip
from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

from sgkit.typing import PathType
from sgkit_vcf.utils import at_eof, get_file_offset, read_bytes


@dataclass
class Chunk:
    cnk_beg: int
    cnk_end: int


@dataclass
class Bin:
    bin: int
    loffset: int
    chunks: Sequence[Chunk]


@dataclass
class CSIIndex:
    min_shift: int
    depth: int
    aux: str
    bins: Sequence[Sequence[Bin]]
    record_counts: Sequence[int]

    def offsets(self) -> Any:
        pseudo_bin = bin_limit(self.min_shift, self.depth) + 1

        file_offsets = []
        contig_indexes = []
        positions = []
        for contig_index, bins in enumerate(self.bins):
            # bins may be in any order within a contig, so sort by loffset
            for bin in sorted(bins, key=lambda b: b.loffset):
                if bin.bin == pseudo_bin:
                    continue  # skip pseudo bins
                file_offset = get_file_offset(bin.loffset)
                position = get_first_locus_in_bin(self, bin.bin)
                file_offsets.append(file_offset)
                contig_indexes.append(contig_index)
                positions.append(position)

        return np.array(file_offsets), np.array(contig_indexes), np.array(positions)


def bin_limit(min_shift: int, depth: int) -> int:
    """Defined in CSI spec"""
    return ((1 << (depth + 1) * 3) - 1) // 7


def get_first_bin_in_level(level: int) -> int:
    return ((1 << level * 3) - 1) // 7


def get_level_size(level: int) -> int:
    return 1 << level * 3


def get_level_for_bin(csi: CSIIndex, bin: int) -> int:
    for i in range(csi.depth, -1, -1):
        if bin >= get_first_bin_in_level(i):
            return i
    raise ValueError(f"Cannot find level for bin {bin}.")  # pragma: no cover


def get_first_locus_in_bin(csi: CSIIndex, bin: int) -> int:
    level = get_level_for_bin(csi, bin)
    first_bin_on_level = get_first_bin_in_level(level)
    level_size = get_level_size(level)
    max_span = 1 << (csi.min_shift + 3 * csi.depth)
    return (bin - first_bin_on_level) * (max_span // level_size) + 1


def read_csi(file: PathType) -> CSIIndex:
    """Parse a CSI file into a queryable datastructure"""
    with gzip.open(file) as f:
        (magic,) = read_bytes(f, "4s")
        if magic != b"CSI\x01":
            raise ValueError("File not in CSI format.")

        min_shift, depth, l_aux = read_bytes(f, "<3i")
        (aux,) = read_bytes(f, f"{l_aux}s", ("",))
        (n_ref,) = read_bytes(f, "<i")

        pseudo_bin = bin_limit(min_shift, depth) + 1

        bins = []
        record_counts = []

        if n_ref > 0:
            for _ in range(n_ref):
                (n_bin,) = read_bytes(f, "<i")
                seq_bins = []
                record_count = -1
                for _ in range(n_bin):
                    bin, loffset, n_chunk = read_bytes(f, "<IQi")
                    chunks = []
                    for _ in range(n_chunk):
                        chunk = Chunk(*read_bytes(f, "<QQ"))
                        chunks.append(chunk)
                    seq_bins.append(Bin(bin, loffset, chunks))

                    if bin == pseudo_bin:
                        assert len(chunks) == 2
                        n_mapped, n_unmapped = chunks[1].cnk_beg, chunks[1].cnk_end
                        record_count = n_mapped + n_unmapped
                bins.append(seq_bins)
                record_counts.append(record_count)

        (n_no_coor,) = read_bytes(f, "<Q", (0,))

        assert at_eof(f)

        return CSIIndex(min_shift, depth, aux, bins, record_counts)
