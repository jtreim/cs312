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

LEFT = 0
TOP = 1

TOP_BANDED = 0
TOP_RIGHT_BANDED = 1

def print_table(alignment_table):
    print('\n\n')
    for i in range(0, len(alignment_table)):
        row = ''
        for j in range(0, len(alignment_table[i])):
            if alignment_table[i][j]:
                entry = '(%s,%s): s:%s a:%s b:%s' % (i, j, alignment_table[i][j][0], alignment_table[i][j][1], alignment_table[i][j][2])
            else:
                entry = '(%s,%s): None' % (i,j)
            row += entry + '\t'
        print(row)
    print('\n\n')

def unrestricted_algorithm(sequence_a, sequence_b, align_length):
    a = sequence_a
    b = sequence_b
    a_idx = 0
    b_idx = 0
    # Allow room for empty character in sequences in alignment table
    longest_sequence = max(len(sequence_a), len(sequence_b))
    table_width = min(align_length+1, longest_sequence+1)

    # Allow for sequence length differences
    if len(sequence_b) <= table_width:
        fill = "-" * (table_width - len(sequence_b))
        sequence_b += fill
    if len(sequence_a) <= table_width:
        fill = "-" * (table_width - len(sequence_a))
        sequence_a += fill

    alignment_table = [[(0, "", "", 0, -1)]]
    for i in range(1, table_width):
        score = i * INDEL
        fill = '-' * i
        alignment_table[0].append((score, fill, fill, INDEL, LEFT))

    for i in range(1, table_width):
        score = i * INDEL
        fill = '-' * i
        row = [(0, fill, fill, INDEL, TOP)]
        char_a = sequence_a[i-1]

        for j in range(1, table_width):
            char_b = sequence_b[j-1]

            # Find best neighboring score
            best_score = row[j-1][0] + INDEL
            best_a = row[j-1][1] + '-'
            best_b = row[j-1][2] + '-'
            action = INDEL
            direction = LEFT

            if alignment_table[i-1][j][0] < best_score:
                best_score = alignment_table[i-1][j][0] + INDEL
                best_a = alignment_table[i-1][j][1] + '-'
                best_b = alignment_table[i-1][j][2] + '-'
                direction = TOP
    
            if (char_a == char_b and alignment_table[i-1][j-1][0] + MATCH < best_score):
                best_score = alignment_table[i-1][j-1][0] + MATCH
                best_a = alignment_table[i-1][j-1][1] + char_a
                best_b = alignment_table[i-1][j-1][2] + char_b
                action = MATCH

            if (char_a != '-' and char_b != '-' and
                alignment_table[i-1][j-1][0] + SUB < best_score):
                best_score = alignment_table[i-1][j-1][0] + SUB
                best_a = alignment_table[i-1][j-1][1] + char_a
                best_b = alignment_table[i-1][j-1][2] + char_b
                action = SUB

            row.append((best_score, best_a, best_b, action, direction))

        alignment_table.append(row)

    return backtrace(alignment_table, table_width - 1, table_width - 1, a, b)

def banded_algorithm(sequence_a, sequence_b, align_length):
    print_at_end = (sequence_a == 'polynomial' or sequence_b == 'exponential')
    d = 3
    table_width = 2*d + 1
    # If difference between a & b is greater than the band width, return inf
    if abs(len(sequence_a) - len(sequence_b)) > align_length:
        return float('inf')

    # Allow room for empty character in sequences in alignment table
    longest_sequence = max(len(sequence_a), len(sequence_b))
    table_height = min(align_length+1, longest_sequence+1)
    alignment_table = [[None for i in range(table_width)] for j in range (table_height)]

    if len(sequence_b) < table_height:
        fill = "-" * (table_height - len(sequence_b))
        sequence_b += fill
    if len(sequence_a) < table_height:
        fill = "-" * (table_height - len(sequence_a))
        sequence_a += fill

    # Populate the first row
    alignment_table[0][d] = (0, "", "")
    for idx in range(d+1, table_width):
        i = idx - d
        score = i * INDEL
        substr = '-' * i
        alignment_table[0][idx] = (score, substr, substr)

    for i in range(1, table_height):
        start = max(d - i, 0)
        rows_left = table_height - i - 1
        if rows_left <= d:
            off = d - rows_left
            end = table_width - off
        else:
            end = table_width 

        char_a = sequence_a[i-1]
        for j in range(start, end):
            offset = j - d
            char_b = sequence_b[i + offset - 1]

            # Find best neighboring score
            best_score = float('inf')
            best_a = ''
            best_b = ''

            # Top MATCH
            if (char_a == char_b and char_a != '-' and alignment_table[i-1][j] is not None and
                best_score > alignment_table[i-1][j][0] + MATCH):
                best_score = alignment_table[i-1][j][0] + MATCH
                best_a = alignment_table[i-1][j][1] + char_a
                best_b = alignment_table[i-1][j][2] + char_b
            
            # Top SUB
            if (char_a != '-' and char_a != '-' and alignment_table[i-1][j] is not None and
                best_score > alignment_table[i-1][j][0] + SUB):
                best_score = alignment_table[i-1][j][0] + SUB
                best_a = alignment_table[i-1][j][1] + char_a
                best_b = alignment_table[i-1][j][2] + char_b

            # Left INDEL
            if (j - 1 >= 0 and alignment_table[i][j-1] is not None and
                best_score > alignment_table[i][j-1][0] + INDEL):
                best_score = alignment_table[i][j-1][0] + INDEL
                best_a = alignment_table[i][j-1][1] + '-'
                best_b = alignment_table[i][j-1][2] + '-'
            
            # Top right INDEL
            if (j + 1 < end and alignment_table[i-1][j+1] is not None and
                best_score > alignment_table[i-1][j+1][0] + INDEL):
                best_score = alignment_table[i-1][j+1][0] + INDEL
                best_a = alignment_table[i-1][j+1][1] + '-'
                best_b = alignment_table[i-1][j+1][2] + '-'

            alignment_table[i][j] = (best_score, best_a, best_b)

    if print_at_end:
        print_table(alignment_table)

    return alignment_table[-1][d]

def backtrace(alignment_table, i, j, a, b):
    score = alignment_table[i][j][0]
    a_align = ''
    b_align = ''
    a_idx = len(a) - 1
    b_idx = len(b) - 1
    while i > 0 and j > 0:
        if alignment_table[i][j][3] == MATCH or alignment_table[i][j][3] == SUB:
            a_align = a[a_idx] + a_align
            b_align = b[b_idx] + b_align
            a_idx -= 1
            b_idx -= 1
            
            if alignment_table[i][j][4] == TOP_BANDED:
                i -= 1
            else:
                i -= 1
                j -= 1

        elif alignment_table[i][j][4] == TOP:
            a_align = '-' + a_align
            i -= 1
            b_idx -= 1
        elif alignment_table[i][j][4] == TOP_RIGHT_BANDED:
            a_align = '-' + a_align
            i -= 1
            j += 1
            b_idx -= 1
        elif alignment_table[i][j][4] == LEFT:
            b_align = '-' + b_align
            j -= 1
            a_idx -= 1

    return (score, a_align, b_align)




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
                    if banded:
                        best_alignment = banded_algorithm(sequences[i], sequences[j], align_length)
                    else:
                        best_alignment = unrestricted_algorithm(sequences[i], sequences[j], align_length)
                    if best_alignment != float('inf'):
                        score = best_alignment[0]
                        a_aligned = best_alignment[1]
                        b_aligned = best_alignment[2]
                    else:
                        score = float('inf')
                        a_aligned = 'None'
                        b_aligned = 'None'
                    alignment1 = '({}, {} chars, align_len={}{})'.format(a_aligned,
                        len(sequences[i]), align_length, ',BANDED' if banded else '')
                    alignment2 = '({}, {} chars, align_len={}{})'.format(b_aligned,
                        len(sequences[j]), align_length, ',BANDED' if banded else '')
###################################################################################################                    
                    s = {'align_cost':score, 'seqi_first100':alignment1, 'seqj_first100':alignment2}
                    table.item(i,j).setText('{}'.format(int(score) if score != math.inf else score))
                    table.repaint()    
                jresults.append(s)
            results.append(jresults)
        return results


