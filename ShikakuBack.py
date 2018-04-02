from __future__ import print_function  # no more Python2 vs Python3 print issue!
import sys
import glob
import time
from rect import rectGet, rectSet, rectTest, rectValid

# These variables should be set during readPuzzle and then never modified.
global rows    # number of rows in the current puzzle
global cols    # number of columns in the current puzzle
global puzzle  # puzzle[row][col] is initial value in (row, col) with -1 for '-'
global anchors # anchors[i] gives the ith anchor as a triple (row, col, value)
global finishTime # the backtracking program must end at this time

# Use this variable to store the current state of the puzzle.  
#  - state[row][col] = i means position (row, col) is covered by anchor i's rectangle.
#  - state[row][col] = -1 means position (row, col) is not covered by a rectangle.
global state


# Read a puzzle stored in a given file name.
# When this function is completed the puzzle variable will store the puzzle 
# as a list of lists, and anchors will be stored as a list of triples.
def readPuzzle(inputFilename):
    global rows, cols, puzzle, anchors
    anchors = []
    with open(inputFilename, "r") as inputFile:
        rows = int(inputFile.readline())
        cols = int(inputFile.readline())
        puzzle = [cols * [""] for i in range(rows)]
        for row, line in enumerate(inputFile):
            for col, symbol in enumerate(line.split()):
                if symbol == "-": 
                    puzzle[row][col] = -1 
                else:
                    puzzle[row][col] = int(symbol)
                    anchors.append((row, col, int(symbol)))

# Verify that the current state is a solution to the current puzzle.
def verifySolution():
    global rows, cols, puzzle, anchors, state
    
    # Verify the following things about each anchor i which is in position (row,col) and has value val.
    #  (1) solution[row][col] should equal i due to the chosen solution format.
    #  (2) the number of i's in solution should equal val.
    #  (3) the i's in solution should form a rectangle.
    for i, (row, col, val) in enumerate(anchors):

        # Verify (1).
        if state[row][col] != i:
            print("error: state[%d][%d] != %d" % (row,col,i), file=sys.stderr)
            return False

        # Get all positions where solution is equal to i.
        wherei = [(r,c) for r in range(rows) for c in range(cols) if state[r][c] == i]
        numi = len(wherei)
             
        # Verify (2).
        if numi != val:
            print("error: state should contain %d copies of %d" % (val,i), file=sys.stderr)
            return False

        # Verify (3).
        left   = min(wherei, key=lambda x: x[0])[0]
        right  = max(wherei, key=lambda x: x[0])[0]
        top    = min(wherei, key=lambda x: x[1])[1]
        bottom = max(wherei, key=lambda x: x[1])[1]
        area = (right-left+1) * (bottom-top+1)
        if area != numi:
            print("error: the %d's in state form a rectangle" % i, file=sys.stderr)
            return False

    return True

def printGrid(grid):
    for row in grid:
        for symbol in row:
            print(str(symbol).rjust(4), end='')
        print("")


def backtrack(nexti):
    global rows, cols, puzzle, anchors, state
    global finishTime

    # Check if we have run out of time.
    if time.time() > finishTime: return
    
    # Initialization.
    if nexti == 0:
        state = [[-1 for c in range(cols)] for r in range(rows)]

   
if __name__ == "__main__":
    global finishTime
    totalSolved = 0
    totalUnsolved = 0
    fileNames = glob.glob("puzzles/*.txt")
    for fileName in fileNames:
        readPuzzle(fileName)
        print(fileName)
        startTime = time.time()
        finishTime = startTime + 100
        backtrack(0)
        endTime = time.time()
        if verifySolution():
            print("solved")
            totalSolved += 1
        else:
            print("not solved")
            totalUnsolved += 1
        print(endTime - startTime)
        print("")
    print("total solved: %d" % totalSolved)
    print("total unsolved: %d" % totalUnsolved)
