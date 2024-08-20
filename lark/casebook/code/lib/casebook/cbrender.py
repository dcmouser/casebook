# Rendering helper class

# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint



class CbRenderDoc:
    def __init__(self):
        self.childManager = CbRenderChildren()

    def printDebug(self):
        jrprint("Debug rendering from CbRenderDoc.")


class CbRenderChildren:
    def __init__(self):
        self.chidren = []
    def addChild(self, child):
        self.children.append(child)


# an entry in document
class CbRenderEntry:
    def __init__(self, entry):
        self.entry = entry
        self.childManager = CbRenderChildren()
        self.contents = None
    def setContents(self, contents):
        self.contents = contents





# my idea is that a render chunk is a lightweight wrapper out of what would otherwise normally be just a string
class CbRenderChunk:
    def __init__(self):
        self.text = None
        pass

















# The CbFiler class is used to help sort and file output sections in a file render book
# derived classes may handle this differently.
# as an example, in New York Noir cases, the CbFilerNyNoir class would create subsections for each # prefix in the leads section
# and in SHCD cases, a CbFilerShcd would create sections for NW, SW, NW, WC, S, etc., and also format lead ids in a consistent way ("25 SW" instead of "SW25") 
# THOUGH perhaps this is best done by options in the parent SECTION options for # LEADS
# and we should let the parent section entry be responsible for creating output rendering sections
class CbFiler:
    def __init__(self):
        pass
