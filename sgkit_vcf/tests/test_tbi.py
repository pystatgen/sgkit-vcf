import pytest

from sgkit_vcf.tbi import read_tabix
from sgkit_vcf.vcf_partition import get_tabix_path
from sgkit_vcf.vcf_reader import count_variants


@pytest.mark.parametrize(
    "vcf_file", ["CEUTrio.20.21.gatk3.4.g.vcf.bgz",],
)
def test_record_counts_tbi(shared_datadir, vcf_file):
    # Check record counts in tabix with actual count of VCF
    vcf_path = shared_datadir / vcf_file
    tabix_path = get_tabix_path(vcf_path)
    tabix = read_tabix(tabix_path)

    for i, contig in enumerate(tabix.sequence_names):
        assert tabix.record_counts[i] == count_variants(vcf_path, contig)


@pytest.mark.parametrize(
    "file",
    ["CEUTrio.20.21.gatk3.4.g.vcf.bgz", "CEUTrio.20.21.gatk3.4.csi.g.vcf.bgz.csi"],
)
def test_read_tabix__invalid_tbi(shared_datadir, file):
    with pytest.raises(ValueError, match=r"File not in Tabix format."):
        read_tabix(shared_datadir / file)
