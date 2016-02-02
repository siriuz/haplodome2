from django.test import TestCase
from ..column_parsers import *


class AccessionsToUniprotUnitTests(TestCase):
    def test_single_accessions_to_uniprot_list(self):
        results = accessions_to_uniprot_list("sp|P04222|1C03_HUMAN")
        assert results == ['P04222']

    def test_multi_accessions_to_uniprot_list(self):
        results = accessions_to_uniprot_list("sp|P04222|1C03_HUMAN;RRRRRsp|Q9UJ78|ZMYM5_HUMAN")
        assert results == ['P04222', 'Q9UJ78']

    def test_invalid_accessions_to_uniprot_list(self):
        results = accessions_to_uniprot_list("a")
        assert results == []

    def test_empty_accessions_to_uniprot_list(self):
        results = accessions_to_uniprot_list("")
        assert results == []


class NamesToProteinDescriptionUnitTests(TestCase):
    def test_single_names_to_protein_descriptions(self):
        results = names_to_protein_descriptions("Uncharacterized protein KIAA1671 OS=Homo sapiens GN=KIAA1671 PE=1 SV=2")
        assert results == ["Uncharacterized protein KIAA1671 OS=Homo sapiens GN=KIAA1671 PE=1 SV=2"]

    def test_multi_names_to_protein_descriptions(self):
        results = names_to_protein_descriptions("Uncharacterized protein KIAA1671 OS=Homo sapiens GN=KIAA1671 PE=1 SV=2;Alkaline extracellular protease OS=Yarrowia lipolytica (strain CLIB 122 / E 150) GN=XPR2 PE=1 SV=1")
        assert results == ["Uncharacterized protein KIAA1671 OS=Homo sapiens GN=KIAA1671 PE=1 SV=2",
                           "Alkaline extracellular protease OS=Yarrowia lipolytica (strain CLIB 122 / E 150) GN=XPR2 PE=1 SV=1"]

    def test_empty_names_to_protein_descriptions(self):
        results = names_to_protein_descriptions("")
        assert results == []


class ModificationsToPtmsDescriptionUnitTests(TestCase):
    def test_single_modifications_to_ptms_descriptions(self):
        results = modifications_to_ptms_descriptions("Deamidated(Q)@7")
        assert results == ["Deamidated(Q)@7"]

    def test_multi_modifications_to_ptms_descriptions(self):
        results = modifications_to_ptms_descriptions("Deamidated(Q)@7;Acetyl@N-term")
        assert results == ["Deamidated(Q)@7",
                           "Acetyl@N-term"]

    def test_empty_modifications_to_ptms_descriptions(self):
        results = modifications_to_ptms_descriptions("")
        assert results == []
