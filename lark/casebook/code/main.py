# interpreter
from lib.casebook.jrinterpCasebook import JrInterpreterCasebook, AstTaskLatex
from lib.casebook.jrastutilclasses import JrAstContext, JrAstEnvironment


# python modules
import sys
import os

# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint





# default grammar files and source files
baseName = "casebook"
rootDirectory = os.path.dirname(os.path.realpath(__file__))
grammarFilePath = rootDirectory + "/grammer/" + baseName + "_grammar.lark"
sourceFilePath = rootDirectory + "/grammer/grammar_test" + "." + baseName

# options
debugMode = True
flagContinueOnException = False
encoding = "utf-8"
startSymbol = "start"





# create context object, which gets our flags
globalContext = JrAstContext(debugMode, flagContinueOnException)
# create global environment, which gets a pointer to our context, and a parent (which is None for root)
globalEnvironment = JrAstEnvironment(globalContext, None)

# interpreter object
jrinterp = JrInterpreterCasebook()




def main():
    # we pass an env environment object around so any function path can access global options about how to report errors, etc.
    env = globalEnvironment

    # commandline grammar file
    if (len(sys.argv)> 1):
        grammarFilePath = sys.argv[1]
    if (len(sys.argv)> 2):
        sourceFilePath = sys.argv[2]


    # PART 1: Parse source file using grammar
    try:
        # PART 1: Ask interpretter to parse
        jrinterp.loadGrammarParseSourceFile(env, grammarFilePath, sourceFilePath, startSymbol, encoding)
    except Exception as e:
        msg = jrfuncs.exceptionPlusSimpleTraceback(e, "Parsing source")
        jrprint(msg)
        return

    # PART 2: Convert parse tree to our interpretter AST class
    jrinterp.convertParseTreeToAst(env)

    # PART 3: Load any core variables and functions into our environment
    jrinterp.setupCasebookStuff(env)

    # PART 4: Run interpretter on a task of our choice
    if (True):
        task = AstTaskLatex()
        jrinterp.taskRenderRun(env, task)

        # test debug
        task.printDebug()



if __name__ == '__main__':
    main()

