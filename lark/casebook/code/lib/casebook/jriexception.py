# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint



# NEW exception which includes source location
class JriException(Exception):
    def __init__(self, message, slocs, severity):
        self.message = message
        self.slocs = slocs
        self.severity = severity

    def __str__(self):
        # create string representation of message in a primitive way, without access to outside info
        slocs = self.slocs
        if (slocs is None):
            # no location info
            return self.message
        else:
            msgs = [self.message]
            if (isinstance(slocs, list)):
                index = 1
                for sloc in slocs:
                    if (sloc is not None):
                        msgs.append("{}. {}".format(index, self.slocInfoStr(sloc)))
                        index += 1
            else:
                sloc = slocs
                if (sloc is not None):
                    msgs.append(self.slocInfoStr(slocs))
        return ";\n".join(msgs)

    def slocInfoStr(self, sloc):
        return makeSlocStringWithNodeTokenDebugInfo(sloc)







def makeJriException(msg, sloc):
    # add node information
    return JriException(msg, sloc, 1)

def logJriWarning(msg, sloc, env):
    # make an exception, but then just display it instead of raising it
    # ATTN: we pass env because we want access to global context so that we can log warnings properly eventually, etc.
    # ATTN: TODO we would like to 
    jri = JriException(msg, sloc, 0)
    jrprint("JRI WARNING:" + msg)









def makeSlocStringWithNodeTokenDebugInfo(sloc):
    from .jrastutilclasses import JrSourceLocation
    from .jrastvals import JrAst

    line = None
    highlightedSourceLine = None
    highlightedSourceLinePos = 0
    rawSourcePath = None
    #
    msg = None
    if (sloc is not None):
        if (isinstance(sloc, JrSourceLocation)):
            # get it from sourceloc object
            line = sloc.getSourceLine()
            start_pos = sloc.getSourceStartPos()
            column = sloc.getSourceColumn()
            msg = "Sloc"
        elif (isinstance(sloc, JrAst)):
            # our jrast tracks this info (using an attached sourceloc)
            line = sloc.getSourceLine()
            start_pos = sloc.getSourceStartPos()
            end_pos = sloc.getSourceEndPos()
            column = sloc.getSourceColumn()
            msg = "AstNode"
            # because we are reporting a JrAst we can get the source line!
            highlightedRawSourceDict = sloc.getRootRawSourceHighlightedLineDict(start_pos, end_pos)
            if (highlightedRawSourceDict is not None) and ("highlightedSourceLineText" in highlightedRawSourceDict):
                highlightedSourceLine = highlightedRawSourceDict["highlightedSourceLineText"]
                highlightedSourceLinePos = highlightedRawSourceDict["highlightedSourceLinePos"]
                highlightedSourceLineEndPos = highlightedRawSourceDict["highlightedSourceLineEndPos"]
                rawSourcePath = highlightedRawSourceDict["path"]
        elif (hasattr(sloc, "_meta")):
            nodeMeta = sloc._meta
            line = nodeMeta.line
            start_pos = nodeMeta.start_pos
            column = nodeMeta.column
            #
            msg = "Token"
            nodeData = sloc.data
            if (hasattr(nodeData,"type")):
                msg += " '{}'".format(nodeData.type)
            elif (type(nodeData) is str):
                msg += "({})".format(nodeData)
            #
            if (hasattr(nodeData,"value")):
                msg += ":'{}'".format(nodeData.value)
        if (line is not None):
            msg += " at line {},col {}".format(line, column)
    if (msg is None):
        msg = "[No source location information available]"
    #
    if (highlightedSourceLine is not None):
        fromStr = "[{}]: ".format(line)
        msg += "\n"+ fromStr + highlightedSourceLine
        highSpaceStr = " " * (highlightedSourceLinePos+len(fromStr))
        highStr = "^" * (highlightedSourceLineEndPos - highlightedSourceLinePos)
        msg += "\n" + highSpaceStr + highStr
    #
    return msg




