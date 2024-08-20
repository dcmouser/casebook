# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint

# jesse lark parser
from lib.jrlark import jrlark

# casebook stuff
from .cbrender import CbRenderDoc

# python
import time

# ast modules
from . import jrastcbr
from .jrastutilclasses import AstTask, DefRmodeRun, DefRmodeRender






# main class
class JrInterpreterCasebook:
    def __init__(self):
        # our itree has SECTION ENTRIES at top level.. but at each level, including root we have a dictionary of two properites ("entries" list, and "entryHash" dict)
        self.ast = jrastcbr.JrAstRootCbr()
        # parser
        self.jrparser = jrlark.JrParserEngineLark()




    def loadGrammarParseSourceFile(self, env, grammarFilePath, sourceFilePath, startSymbol, encoding):
        # PART 1: Load casebook grammar from .lark file
        self.jrparser.loadGrammarFileFromPath(env, grammarFilePath, encoding)
        # PART 2: parse source file
        self.jrparser.parseSourceFromFilePath(env, sourceFilePath, startSymbol, encoding)



    def setupCasebookStuff(self, env):
        # setup built-in vars
        self.ast.setupBuiltInVars(env)
        # setup built-in core functions
        self.ast.loadCoreFunctions(env)




    def convertParseTreeToAst(self, env):
        start_time = time.perf_counter()

        # get data from parser
        rawSourceDict = self.jrparser.getRawSourceDict()
        parseTree = self.jrparser.getParseTree()

        # convert parse tree to our AST
        self.ast.setRawSourceDict(rawSourceDict)
        self.ast.convertParseTreeToAst(env, parseTree)

        # report elapsed time?
        if (env.getDebugMode()):
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            self.printDebug()
            jrprint("Elapsed time to run convert parseTree (): {}.".format(jrfuncs.niceElapsedTimeStr(elapsed_time)))

        return self.ast


    def printDebug(self):
        jrprint("Created Abstract Syntax Tree (AST):")
        self.ast.printDebug(1)




    def taskRenderRun(self, env, task):
        # just pass it off to the ast
        self.ast.taskRenderRun(env, task)


























# task helpers

class AstTaskLatex(AstTask):
    def __init__(self):
        super().__init__("latex", DefRmodeRender)
        self.setRenderFormat("latex")
        self.setRenderer(CbRenderDoc())


