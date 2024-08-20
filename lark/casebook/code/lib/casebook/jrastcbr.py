# ast modules
from . import jrast
from .jrastfuncs import wrapDictForAstVal, wrapObjectForAstVal

# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint



# derived class that adds output rendering

class JrAstRootCbr(jrast.JrAstRoot):
    def __init__(self):
        super().__init__()


    def setupBuiltInVars(self, env):
        # test
        info = {
            "name": None,
            "title": None,
            "subtitle": None,
            "authors": None,
            "version": None,
            "versionDate": None,
            "difficulty": None,
            "duration": None,
            "cautions": None,
            "summary": None,
            "extraInfo": None,
            "url": None,
        }

        game = {
            "clocked": None,
            "clockTimeStep": None,
            "clockTimeDefaultLead": None,
        }

        data = {
            "version": None,
            "versionPrevious": None,
        }

        parser = {
            "autoStyleQuotes": True,
            "disabledBalancedQuoteCheck": False,
        }

        # register these python objects with runtime environment
        env.declareEnvVar(None, "info", "information about the game", wrapDictForAstVal(None, info), False)
        env.declareEnvVar(None, "game", "game settings", wrapDictForAstVal(None, game), False)
        env.declareEnvVar(None, "data", "highlow data settings", wrapDictForAstVal(None, data), False)
        env.declareEnvVar(None, "parser", "parser settings", wrapDictForAstVal(None, parser), False)
