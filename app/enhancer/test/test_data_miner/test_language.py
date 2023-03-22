import unittest
import sys,os
sys.path.insert(0, os.path.join("..","..","..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
sys.path.insert(0, os.path.join("..",".."))

from app.enhancer.data_miner.language.analyser import LanguageAnalyser

class TestLanguageAnalyser(unittest.TestCase):

    def setUp(self):
        self.language_analyser = LanguageAnalyser()

    def tearDown(self):
        None

    def test_mine_sentences(self):
        sentences = "This plasmid consists of the mcherry gene (encoding red fluorescence protein) inserted in the backbone of pAW50 vector. EcoRI-NotI-XbaI-NsiI restriction sites have been introduced followed by a linker sequence followed by the mcherry sequence. The use of these sites will allow users to introduce any desired gene of their choice to be fused with the linker which is already fused with the mcherry sequence. This way any protein can be qualitatively studied in Methanogens via red fluorescence. Note:- the users will have to introduce the RBS sequence and start codon, delete the terminator sequence of their gene while cloning. Primer were designed in a way to introduce EcoRI-NotI-XbaI-NsiI sites before the linker. mcherry was obtained from Discosoma sp."
        res = self.language_analyser.get_subjects(sentences)
        self.assertIn("plasmid",res)
if __name__ == '__main__':
    unittest.main()
