# lark
import lark

# jrast
from .jrastfuncs import wrapValIfNotAlreadyWrapped
from .jrastvals import AstValObject
from .jriexception import *


# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint


# python modules
import traceback


# defines
# we can set this False if we want to try to save a little memory
DefAlwaysStoreContextInEveryEnvironment = True

# render run modes
DefRmodeRun = "run"
DefRmodeRender = "render"







# for tracking source location of tokens
class JrSourceLocation:
    def __init__(self, sloc=None):
        #
        self.copyFrom(sloc)

    def clearLocation(self):
        self.start_pos = -1
        self.end_pos = -1
        self.line = -1
        self.column = -1
        self.end_line = -1
        self.end_column = -1

    def copyFrom(self, fromObj):
        if (fromObj is None):
            # blank
            self.clearLocation()
            return
        
        if (isinstance(fromObj, lark.Tree)):
            # lark tree has token as data
            sloc = fromObj.meta

        if (not hasattr(fromObj,"start_pos") and (hasattr(fromObj,"meta"))):
            fromObj = fromObj.meta

        if (hasattr(fromObj,"start_pos")):
            # already a JrSourceLocation; copy from it?
            # or its a lark token type see https://lark-parser.readthedocs.io/en/latest/classes.html#token
            self.line = fromObj.line
            self.start_pos = fromObj.start_pos
            self.end_pos = fromObj.end_pos
            self.column = fromObj.column
            self.end_line = fromObj.end_line
            self.end_column = fromObj.end_column
            return
        if (hasattr(fromObj,"getSourceLine")):
            # already a JrSourceLocation; copy from it?
            # or its a lark token type see https://lark-parser.readthedocs.io/en/latest/classes.html#token
            self.line = fromObj.getSourceLine()
            self.start_pos = fromObj.getSourceStartPos()
            self.end_pos = fromObj.getSourceEndPos()
            self.column = fromObj.getSourceColumn()
            self.end_line = fromObj.getSourceEndLine()
            self.end_column = fromObj.getSourceEndColumn()
            return

        
        if (isinstance(fromObj, lark.Token) or isinstance(fromObj, lark.tree.Meta)):
            # no line number attribues for this particular token it seems
            self.clearLocation()
            return

        # error and we don't know how to report where the problem is
        msg = "Internal interpretter error; sloc info was not understood ({}).".format(fromObj)
        raise makeJriException(msg, None)

    def debugString(self):
        str = "line {}:{}".format(self.line, self.column)
        return str

    
    def getSourceLine(self):
        return self.line
    def getSourceStartPos(self):
        return self.start_pos
    def getSourceEndPos(self):
        return self.end_pos
    def getSourceColumn(self):
        return self.column
    def getSourceEndLine(self):
        return self.end_line
    def getSourceEndColumn(self):
        return self.end_column



















































# A note on JrAstContext vs JrAstEnvironment

# an Environment object is a storage of state information -- variable assignments
# it is hierarchical so supports SCOPED resolution of variables where we may have a chain of scopes and want to find a variable in the closest scope
# as such, it is a RUNTIME data structure; it is the primary data structure that we pass around the hierarchy when we are executing code
# and we may create new child environments on the fly
# you could even imagine (though we do not do it currently) running multiple functions in parallel with different environments using the same ast tree
# JrAstContext is more of a single global object that holds some global options, which are not normally accessible directly through casebook code
# there is only one JrAstContext for an app.
# we can think of it as some special reserverd data in the highest level environment




class JrAstContext:
    def __init__(self, debugMode, flagContinueOnException):
        self.debugMode = debugMode
        self.flagContinueOnException = flagContinueOnException
        #
        self.exceptionTracebackLimit = 1


    def setDebugMode(self, debugMode):
        self.debugMode = debugMode
    def getDebugMode(self):
        return self.debugMode
    def getFlagContinueOnException(self):
        return self.flagContinueOnException

    def displayException(self, e):
        tracebackLimit = self.exceptionTracebackLimit
        if (tracebackLimit >= 0):
            tracebackLines = traceback.format_exception(e, limit = tracebackLimit)
            tracebackText = "\n".join(tracebackLines)
        else:
            tracebackText = "disabled"
        #
        jrprint("CONTINUING AFTER EXCEPTION: {}.  Traceback: {}.".format(repr(e), tracebackText))















































# An environment is a dictionary of variable assignments, with a pointer to parent enclosing environment
class JrAstEnvironment:
    def __init__(self, context, parentEnv):
        self.parentEnv = parentEnv
        #
        # we can avoid storing context in every sub child environment if we like, to save memory space?
        if (DefAlwaysStoreContextInEveryEnvironment) or (parentEnv is None):
            self.context = context
        #
        self.envDict = {}
        #
        # create task
        self.declareEnvVar(None, "task", "", None, True)


    def getDebugMode(self):
        return self.getContext().getDebugMode()
    def getFlagContinueOnException(self):
        return self.getContext().getFlagContinueOnException()
    




    # environmental variables (note that on set we just overwrite)

    # NOTE: identifier names can be DOTTED hierarchies inside objects; we need to handle that

    # lookup env var and go up hierarchy if needed
    def lookupJrEnvVar(self, sloc, identifierName, flagGoUpHierarchy):
        # return [envVar, baseName, partList]

        # split identifier into base and parts
        [baseVarName, propertyParts] = self.splitIndentifierParts(identifierName)

        if (baseVarName in self.envDict):
            # its defined locally; return the triplet
            return [self.envDict[baseVarName], baseVarName, propertyParts]
        if (flagGoUpHierarchy) and (self.parentEnv is not None):
            # search up hierarchy of environments
            return self.parentEnv.lookupJrEnvVar(sloc, identifierName, True)

        # not found
        return [None, None, None]


    def splitIndentifierParts(self, identifierName):
        parts = identifierName.split(".")
        if (len(parts)==0):
            return [None, None]
        if (len(parts)==1):
            return [parts[0], None]
        return [ parts[0], parts[1:] ]


    # declare var in THIS env scope
    def declareEnvVar(self, sloc, identifierName, description, val, isConstant):
        [envVar, baseName, partList] = self.lookupJrEnvVar(sloc, identifierName, False)
        # first, complain if they try to DECLARE a dotted name
        if (partList is not None):
            raise self.makeEnvException("Error; dotted object identifiers ({}) cannot be declared".format(identifierName), sloc)
        if (envVar is not None):
            # error already exists
            raise self.makeEnvExceptionWithPreviousValue("Runtime error; identifier '{}' already exists in current environment scope and so cannot be redeclared".format(identifierName), sloc, envVar)
        # ATTN: note that we dont complain if we are shadowing a parent env variable, but we COULD add a warning for it if we wanted
        if (True):
            [envVar, baseName, partList] = self.lookupJrEnvVar(sloc, identifierName, True)
            if (envVar is not None):
                # warning
                self.logEnvWarningWithPreviousValue("Runtime warning; declaring a variable '{}' which will shadow an existing variable in parent scope".format(identifierName), sloc, envVar)
        # create it
        self.envDict[identifierName] = JrEnvVar(sloc, identifierName, description, val, isConstant)


    # set a value; NOTE we require all variables to be declared before use so this is an error if it cannot be found in scope -- it won't be creatded
    def setEnvValue(self, sloc, identifierName, val, flagCheckConst):
        [envVar, baseName, partList] = self.lookupJrEnvVar(sloc, identifierName, True)
        if (not envVar):
            # error does not exist
            raise self.makeEnvException("Runtime error; identifier '{}' has not been declared in this or any parent scope".format(identifierName), sloc)
        if (flagCheckConst and envVar.getIsConstant()):
            raise self.makeEnvExceptionWithPreviousValue("Runtime error; identifier {} has been declared constant and so cannot be reassigned".format(identifierName), sloc, envVar)
        # set the non-const value
        envVar.setValue(sloc, partList, val, flagCheckConst)



    def getEnvValue(self, sloc, identifierName, defaultVal):
        [envVar, baseName, partList] = self.lookupJrEnvVar(sloc, identifierName, True)
        if (envVar is None):
            # not found
            return defaultVal
        # ask the envvar for its value
        retVal = envVar.getWrappedValue(sloc, partList)
        return retVal




    def loadFuncsFromModule(self, sloc, module):
        functionList = module.buildFunctionList()
        self.loadFuncsFromList(sloc, functionList)

    def loadFuncsFromList(self, sloc, functionList):
        from .jrastvals import AstValFunction

        for func in functionList:
            funcName = func.getName()
            funcVal = AstValFunction(None, None, func)
            funcDescription = funcVal.getDescription()
            self.declareEnvVar(sloc, funcName, funcDescription, funcVal, False)

    def getContext(self):
        # this code allows us to ONLY store context with top level global env
        if (hasattr(self, "context")):
            return self.context
        if (self.parentEnv is not None):
            # recurse up to get context
            return self.parentEnv.getContext()
        # not found
        return None

    def makeChildEnv(self):
        # create a child environment
        childEnv = JrAstEnvironment(self.context, self)
        return childEnv



    def makeEnvException(self, msg, sloc):
        return makeJriException(msg, sloc)

    def makeEnvExceptionWithPreviousValue(self, msg, sloc, prevEnvVar):
        # ATTN: ADD source info from prevEnvVar
        return makeJriException(msg, [sloc, prevEnvVar.getSloc()])

    def logEnvWarningWithPreviousValue(self, sloc, msg, prevEnvVar):
        # ATTN: ADD source info from prevEnvVar and source info, etc.
        logJriWarning(msg, [sloc, prevEnvVar.getSloc()], self)



    def getTask(self):
        return self.getEnvValue(None, "task", None)
    def setTask(self, task):
        return self.setEnvValue(None, "task", task, False)










class JrEnvVar:
    # holds a variable/constant that can be in the environment, and enforces constantness
    # note like most of Casebook runtime, this is a heavy weight object that keeps track of the source location where it was set from and its on parent env
    # in this way, a variable knows "where" in the source code its last value was asigned, etc.
    # so memory use is much higher than strictly needed, in order to support robust error reporting; this is ok for Casebook language tradeoff
    #
    # ON THE OTHER HAND: it seems like a lot of duplicity here, in that an EnvVar wraps as AtstVal which ALSO has env, sloc info; some of this seems very duplicative
    #
    def __init__(self, sloc, name, description, initialValue, isConstant):
        self.sloc = sloc
        self.name = name
        self.description = description
        self.value = None
        self.isConstant = False
        #
        self.setValue(sloc, None, initialValue, False)
        self.isConstant = isConstant



    def getStoredValue(self, sloc, partList):
        # if partList is empty, then we want our value, otherwise we want oject property
        if (partList is None):
            return self.value
        else:
            # we require a wrapped python OBJECT for dotted path resolution
            # ATTN: should we use passed sloc or getSloc of ourselves?
            val = self.value.getProperty(self.getSloc(), self.getName(), partList)
            return val

    def setValue(self, sloc, partList, val, flagCheckConst):
        # if partList is empty, then we want to set our value, otherwise we want oject property
        if (flagCheckConst and self.isConstant):
            msg = "Runtime error; variable {} is defined as constant with current value({}); cannot be set to new value ({})".format(self.name, self.getStoredValue(sloc, partList), val)
            raise self.makeEnvVarException(msg, sloc)
        #
        wrappedVal = wrapValIfNotAlreadyWrapped(None, None, val)

        # if partList is empty, then we want to set our value, otherwise we want oject property
        if (partList is None):
            self.value = wrappedVal
        else:
            # we require a wrapped python OBJECT for dotted path resolution
            return self.value.setProperty(sloc, self.getName(), partList, wrappedVal)



    def getWrappedValue(self, sloc, partList):
        val = self.getStoredValue(sloc, partList)
        return wrapValIfNotAlreadyWrapped(sloc, None, val)


    def getIsConstant(self):
        return self.isConstant

    def getSloc(self):
        return self.sloc
    def getName(self):
        return self.name


    def makeEnvVarException(self, msg, sloc):
        # ATTN: TODO can we add source location info?
        return makeJriException(msg, [sloc, self.getSloc()])

















class AstTask:
    def __init__(self, taskId, rMode):
        self.taskId = taskId
        self.rMode = rMode
        self.renderer = None
        self.renderFormat = None
    def getTaskId(self):
        return self.taskId
    def getRmode(self):
        return self.rMode
    def getRenderFormat(self):
        return self.renderFormat
    def setRenderFormat(self, renderFormat):
        self.renderFormat = renderFormat
    def setRenderer(self, renderer):
        self.renderer = renderer
    def getRenderer(self):
        return self.renderer

    def printDebug(self):
        self.getRenderer().printDebug()
