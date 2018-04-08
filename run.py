from __future__ import print_function  # no more Python2 vs Python3 print issue!
import sys
import glob
import time
import copy
# for factors:
from functools import reduce

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


def getFactors(n):
    return set(reduce(list.__add__,
                ([i, n//i] for i in range(1, int(pow(n, 0.5) + 1)) if n % i == 0)))


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
    # anchors.sort(key=lambda x: x[2])


# Verify that the current state is a solution to the current puzzle.
def verifySolution():
    global rows, cols, puzzle, anchors, state

    print("Final State")
    printGrid(state)

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


def unplaceRect(rect, last=None):
    global rows, cols, puzzle, anchors, state

    (dim, start, og) = rect
    # number to place on each box
    n = dim[0]*dim[1]

    if last == None:
        last = (dim[0], dim[1])

    # for each row
    for i in range(dim[0]):
        # for each column
        for j in range(dim[1]):
            # we skip the square that already has our n on it (og has the coord)
            if i+start[0] == og[0] and j+start[1] == og[1]:
                continue
            # every other square should be 0
            if i < last[0] or j < last[1]:
                state[i+start[0]][j+start[1]] = -1
            else:
                return
    return



def placeRect(rect, nexti):
    """
    Attempts to place rect and returns status (True or False)
    """
    global rows, cols, puzzle, anchors, state

    (dim, start, og) = rect
    # number to place on each box
    n = dim[0]*dim[1]


    # for each row
    for i in range(dim[0]):
        # for each column
        for j in range(dim[1]):
            # we skip the square that already has our n on it (og has the coord)
            if i+start[0] == og[0] and j+start[1] == og[1]:
                continue
            # every other square should be -1
            if state[i+start[0]][j+start[1]] == -1:
                state[i+start[0]][j+start[1]] = nexti
            else:
                # if not, we cannot place here
                unplaceRect(rect, (i, j))
                return False
    return True



def createRects(anchor):
    """
    Args:
        anchor: inform of (row, col, n)
    Returns:
        list of rects: in form of ((nrows, ncols), (start pos coords), (num pos coords))
    """
    global rows, cols, puzzle, anchors, state
    # n is the number of elements in the rect
    n = anchor[2]
    # get factors of n
    factors = getFactors(n)

    # create p x q tuples
    dims = []
    for i in factors:
        dims.append((i, int(n/i)))

    # generate possible positions for each
    rects = []
    for dim in dims:
        for i in range(dim[0]):
            for j in range(dim[1]):
                # push the rectangle back to the limits (i and j)
                start = (anchor[0]-i,anchor[1]-j)
                if start[0] >= 0 and start[1] >= 0 and start[0] + dim[0] <= rows and start[1] + dim[1] <= cols:
                    og = (anchor[0], anchor[1])
                    rects.append((dim, start, og))
    # print("rects")
    # print(rects)
    return rects


def finalFill():
    global rows, cols, puzzle, anchors, state
    for i in range(len(anchors)):
        state[anchors[i][0]][anchors[i][1]] = i


def backtrack(nexti):
    """
    MAIN ALGORITHM
    """
    global rows, cols, puzzle, anchors, state
    global finishTime
    global isSolved

    # Check if we have run out of time.
    if time.time() > finishTime or isSolved == True:
        return

    # Initialization.
    if nexti == 0:
        # state = [[-1 for c in range(cols)] for r in range(rows)]
        state = copy.deepcopy(puzzle)



    # More backtrack calls
    rects = createRects(anchors[nexti])
    for rect in rects:
        if isSolved == True:
            return
        # will return true if rect was successfully placed
        if placeRect(rect, nexti):
            # check if last anchor => check solution
            if nexti + 1 >= len(anchors):
                finalFill()
                isSolved = True
                return
            else:
                backtrack(nexti+1)
                if isSolved == True:
                    return
                else:
                    unplaceRect(rect)





if __name__ == "__main__":
    global isSolved
    global finishTime
    totalSolved = 0
    totalUnsolved = 0
    fileNames = glob.glob("puzzles/*.txt")
    fileNames.sort()
    for fileName in fileNames:
        readPuzzle(fileName)
        print(fileName)
        startTime = time.time()
        duration = 100
        finishTime = startTime + duration
        isSolved = False
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
