from Bio import Align
from Bio.Seq import Seq

class Aligner:
    def __init__(self):
        self._aligner = Align.PairwiseAligner()
        self._aligner.mode = 'global'
        self._aligner.substitution_matrix = Align.substitution_matrices.load("BLOSUM62")
        self._aligner.match_score = 1.0 
        self._aligner.mismatch_score = -1.0

    def sequence_match(self,seq1,seq2):
        seq1 = Seq(seq1.lower())
        seq2 = Seq(seq2.lower())
        return self._aligner.score(seq2,seq1)/len(max([seq2,seq1], key=len))
