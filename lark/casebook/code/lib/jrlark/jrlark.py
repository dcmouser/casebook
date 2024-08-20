# lark
from lark import Lark, tree, logger, UnexpectedInput

# python
import os
import time

# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint




# main class
class JrParserEngineLark:
    def __init__(self):
        #
        self.grammarFilePath = None
        self.sourceFilePath = None
        #
        self.grammarText = None
        self.sourceText = None
        #
        self.parseTree = None
        #
        # see https://lark-parser.readthedocs.io/en/latest/classes.html
        # lexer:
        #   “auto” (default): Choose for me based on the parser
        #   “basic”: Use a basic lexer
        #   “contextual”: Stronger lexer (only works with parser=”lalr”)
        #   “dynamic”: Flexible and powerful (only with parser=”earley”)
        #   “dynamic_complete”: Same as dynamic, but tries every variation of tokenizing possible.
        # amgiguity:
        #    • “resolve”: The parser will automatically choose the simplest derivation (it chooses consistently: greedy for tokens, non-greedy for rules)
        #    • “explicit”: The parser will return all derivations wrapped in “_ambig” tree nodes (i.e. a forest).
        #    • “forest”: The parser will return the root of the shared packed parse forest
        self.options = {
            "parser": "earley",
            "ambiguity": "resolve",
            "lexer": "auto",

            #"parser": "lalr",
            #"ambiguity": None,
            #"lexer": "contextual",

            # default start symbol, can be overridden during call to parse
            "start": "start",
            #"start": "overview_start",
            "strict": False, # only applies to LALR parser, ignored for earley

            # debug true is causing a syntax error when it tries to use pydot to create an image diagram of parse (something to do with \r\n syntax error)
            "larkDebug": False,
            "diagrams": False,

            # see syntax for creating None token on missing [] rule
            "maybe_placeholders": True,

            "propagate_positions": True,
            "regex": True
        }
    


    def loadGrammarFileFromPath(self, env, grammarFilePath, encoding):
        self.grammarFilePath = grammarFilePath
        grammarText = jrfuncs.loadTxtFromFile(self.grammarFilePath, True, encoding=encoding)
        self.grammarText = grammarText

    def loadSourceFromFilePath(self, sourceFilePath, encoding):
        self.sourceFilePath = sourceFilePath
        text = jrfuncs.loadTxtFromFile(self.sourceFilePath, True, encoding=encoding)
        self.sourceText = text
        return text

    def parseSourceFromFilePath(self, env, sourceFilePath, startSymbol, encoding):
        sourceText = self.loadSourceFromFilePath(sourceFilePath, encoding)
        self.parseTree = self.parseText(env, sourceText, startSymbol)
        return self.parseTree

    def getRawSourceDict(self):
        # just return the raw source loaded from file, etc.
        return {"path": self.sourceFilePath, "text": self.sourceText}

    def getParseTree(self):
        return self.parseTree

    def buildParser(self):
        larkDebug = self.options["larkDebug"]
        if (larkDebug):
            import logging
            logger.setLevel(logging.DEBUG)
        self.parser = Lark(self.grammarText, parser = self.options["parser"], start=self.options["start"], ambiguity=self.options["ambiguity"], lexer=self.options["lexer"], strict=self.options["strict"], debug=larkDebug, propagate_positions=self.options["propagate_positions"], regex=self.options["regex"])
        return self.parser




    def parseText(self, env, text, startSymbol):
        # build parser using self options
        #
        self.options["start"] = startSymbol
        parser = self.buildParser()

        # parse and get result
        start_time = time.perf_counter()
        try:
            parseResult = parser.parse(text)
        except UnexpectedInput as u:
            handled = self.handleExceptionUnexpectedInput(parser, text, u)
            if (not handled):
                raise u
        except Exception as e:
            print("Caught an unknown exception while parsing: ")
            print(e)
            raise e

        # report elapsed time
        end_time = time.perf_counter()

        # display pretyy result
        if (env.getDebugMode()):
            parseResultPretty = parseResult.pretty()
            jrprint(parseResultPretty)
            elapsed_time = end_time - start_time
            jrprint("Total time to parse ({}): {}.".format(startSymbol, jrfuncs.niceElapsedTimeStr(elapsed_time)))

        # generate diagrams
        if (self.options["diagrams"]):
            diagramOutputFilePath = jrfuncs.createSisterFileName(self.sourceFilePath,"_diagram")
            self.makeDiagrams(parseResult, diagramOutputFilePath)

        return parseResult



    # helper for making parse tree diagrams
    def makeDiagrams(self, parseResult, outputFilePath):
        tree.pydot__tree_to_png( parseResult, outputFilePath+".png")
        tree.pydot__tree_to_dot( parseResult, outputFilePath+".dot")














    # ATTN: this does not work well enough to be useful for us; i'm leaving code in but it is not being used

    def handleExceptionUnexpectedInput(self, parser, text, u):
        # return true if its handled, otherwise raise something else or return False

        pretextList = ["# OPTIONS\n", "# id\n", "# OPTIONS\n", "# id\n",]
        pretext1 = "# OPTIONS\n"
        pretext2 = "# header\n## childheader\n"

        exc_class = u.match_examples(parser.parse, {
            JrParserSyntaxError_MissingColonAfterIfElseBrace: [
                pretext2 + '$if(true) {}',
                pretext2 + '$if(true) {',
                ],
            JrParserSyntaxError_MissingColonAfterIfGenericFunction: [
                pretext2 + '$func() {}',
                pretext2 + '$func() {',
                pretext2 + '$mybadfunc("age") { Hello world. }',
                pretext1 + '$if\n (true):\n You are $var("age") years old. $else: You are $format(font="typewriter"): too young.\n\n$mybadfunc("age") { Hello world. }',
                ],
        }, use_accepts=True)
        if not exc_class:
            raise
        raise exc_class(u.get_context(text), u.line, u.column)

# helpers for error reporting
class JrParserSyntaxError(SyntaxError):
    def __str__(self):
        context, line, column = self.args
        return "%s at line %s, column %s.\n\n%s" % (self.label, line, column, context)

class JrParserSyntaxError_MissingColonAfterIfElseBrace(JrParserSyntaxError):
    label = "Are you missing a colon (:) between the if/elif/else condition test and the action to perform?"

class JrParserSyntaxError_MissingColonAfterIfGenericFunction(JrParserSyntaxError):
    label = "Are you missing a colon (:) between the function call and the text to operate on?"




