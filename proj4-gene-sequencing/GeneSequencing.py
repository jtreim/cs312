#!/usr/bin/python3

#from PyQt5.QtCore import QLineF, QPointF



import math
import time

# Used to compute the bandwidth for banded version
MAXINDELS = 3

# Used to implement Needleman-Wunsch scoring
MATCH = -3
INDEL = 5
SUB = 1

class AlignmentScore:
    def __init__(self, score, alignment):
        self.score = score
        self.alignment = alignment


def can_match(char_a, char_b):
    return char_a == char_b and char_a != '-'
def can_sub(char_a, char_b):
    return char_a != '-' and char_b != '-'

def print_table(alignment_table):
    print('\n\n')
    for i in range(0, len(alignment_table)):
        row = ''
        for j in range(0, len(alignment_table[i])):
            if alignment_table[i][j]:
                entry = '(%s,%s): s:%s a:%s' % (i, j, alignment_table[i][j].score, alignment_table[i][j].alignment)
            else:
                entry = '(%s,%s): None' % (i,j)
            row += entry + '\t'
        print(row)
    print('\n\n')

def unrestricted_algorithm(sequence_a, sequence_b, align_length):
    # Allow room for empty character in sequences in alignment table
    alignment_table = [[None for i in range(align_length+1)] for j in range (align_length+1)]

    # print_table(alignment_table)

    if len(sequence_b) < align_length:
        fill = "-" * (align_length - len(sequence_b))
        sequence_b += fill
    if len(sequence_a) < align_length:
        fill = "-" * (align_length - len(sequence_a))
        sequence_a += fill

    # Populate the first row and column
    alignment_table[0][0] = AlignmentScore(0, "")
    # print('(0,0): s:%s a:%s' % (alignment_table[0][0].score, alignment_table[0][0].alignment))
    for i in range(1, align_length+1):
        score = i * INDEL
        substr = '-' * i
        alignment_table[0][i] = AlignmentScore(score, substr)
        alignment_table[i][0] = AlignmentScore(score, substr)

    # print_table(alignment_table)

    i = 1
    while i <= align_length:
        char_a = sequence_a[i-1]
        for j in range(i, align_length+1):
            char_b = sequence_b[j-1]

            # print('i: %s\tj: %s' % (i, j))
            # print('char_a: %s\tchar_b: %s' % (char_a, char_b))

            # Find best neighboring score
            left = alignment_table[i][j-1]
            top = alignment_table[i-1][j]
            diagonal = alignment_table[i-1][j-1]

            # Apply best change
            # No need to add changes
            if char_a == '-' and char_b == '-':
                # print('a and b are both blank! No need to do anything.')
                alignment_table[i][j] = AlignmentScore(diagonal.score, diagonal.alignment)
                alignment_table[j][i] = AlignmentScore(diagonal.score, diagonal.alignment)
            else:
                best = AlignmentScore(left.score + INDEL, left.alignment + '-')
                if top.score < best.score:
                    best.score = top.score + INDEL
                    best.alignment = top.alignment + '-'
                
                if can_match(char_a, char_b) and diagonal.score + MATCH < best.score:
                    # print('Best score found to be matching %s and %s!\nResulting score: %s' % (char_a, char_b, (diagonal.score + MATCH)))
                    # print('Resulting alignment: %s' % (diagonal.alignment + char_a))
                    best.score = diagonal.score + MATCH
                    best.alignment = diagonal.alignment + char_a
                if can_sub(char_a, char_b) and diagonal.score + SUB < best.score:
                    # print('Best score found to be substituting %s and %s!\nResulting score: %s' % (char_a, char_b, (diagonal.score + SUB)))
                    # print('Resulting alignment: %s' % (diagonal.alignment + char_a))
                    best.score = diagonal.score + SUB
                    best.alignment = diagonal.alignment + char_a
                alignment_table[i][j] = AlignmentScore(best.score, best.alignment)
                alignment_table[j][i] = AlignmentScore(best.score, best.alignment)
        i += 1
    
    return alignment_table[align_length][align_length]

            


class GeneSequencing:

    def __init__( self ):
        pass

# This is the method called by the GUI.  _sequences_ is a list of the ten sequences, _table_ is a
# handle to the GUI so it can be updated as you find results, _banded_ is a boolean that tells
# you whether you should compute a banded alignment or full alignment, and _align_length_ tells you 
# how many base pairs to use in computing the alignment
    def align( self, sequences, table, banded, align_length ):
        self.banded = banded
        self.MaxCharactersToAlign = align_length
        results = []

        for i in range(len(sequences)):
            jresults = []
            for j in range(len(sequences)):
                if j < i:
                   s = {}
                else:
###################################################################################################
# your code should replace these three statements and populate the three variables: score, alignment1 and alignment2
                    best_alignment = unrestricted_algorithm(sequences[i], sequences[j], align_length)
                    score = best_alignment.score
                    alignment1 = 'abc-easy  DEBUG:(seq{}, {} chars,align_len={}{})'.format(i+1,
                        len(sequences[i]), align_length, ',BANDED' if banded else '')
                    alignment2 = 'as-123--  DEBUG:(seq{}, {} chars,align_len={}{})'.format(j+1,
                        len(sequences[j]), align_length, ',BANDED' if banded else '')
###################################################################################################                    
                    s = {'align_cost':score, 'seqi_first100':alignment1, 'seqj_first100':alignment2}
                    table.item(i,j).setText('{}'.format(int(score) if score != math.inf else score))
                    table.repaint()    
                jresults.append(s)
            results.append(jresults)
        return results


