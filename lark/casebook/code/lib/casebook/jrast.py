# AST = Abstract Syntax Tree

# ast util classes
from .cblarkdefs import *

# these are our main ast work class so we bring in all helpers
from .jrastutilclasses import *
from .jrastfuncs import *
from .jrastvals import *
from .jriexception import *

# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint


# other defines
JrCb_blankEntryId = ""
DefEntryIdOptions = "OPTIONS"
DefEntryIdSetup = "SETUP"
DefEntryIdCover = "COVER"
DefSpecialEntryIdsAlwaysRun = [DefEntryIdOptions, DefEntryIdSetup, DefEntryIdCover]




# A note on why most functions pass an env object:
# Most functions pass along an env variable , which holds not only a hierarchical scope of identifier indexed data store
# But only a reference to a global context object which is used for global options (like debug settings)
# We pass this around because we consider that it may be useful to have access to these options which would otherwise have to be defined as global
# Any function (or constructor) that might want to raise an exception (or call a function that might), needs to be passed an env object so that it can access such (semi-global) structures
# We *originally* kept a simple pointer to a semi-global context object inside the JrAst nodes so that we would not have to continually pass it around
# The "problem" with this approach is that, while in practice this should work fine, its "ugly" in the sense that the JrAst nodes are static structures that could conceivably be run in parallel with different context structures
# Regardless, one can consider that the env object carries with it all contextual information that might be useful in reporting/recording errors 











































# root
class JrAstRoot (JrAst):
    def __init__(self):
        super().__init__(None, None)
        #
        self.prelimaryMatter = None
        self.endMatter = None
        #
        self.rawSourceDict = None
        #
        self.entries = JrAstEntryChildHelper(None, self)



    def printDebug(self, depth):
        # nice hierarchical tabbed pretty print
        super().printDebug(depth)
        # and now our entries
        self.entries.printDebug(depth+1)


    def loadCoreFunctions(self, env):
        # load functions from module
        from . import cbfuncs_core 
        env.loadFuncsFromModule(None, cbfuncs_core)


    def setRawSourceDict(self, rawSourceDict):
        # store raw source for reporting errors
        self.rawSourceDict = rawSourceDict


    def convertParseTreeToAst(self, env, parseTree):
        # given a LARK parse tree, convert it into OUR AST format

        # we go through a process of restructuring the parse tree to build a kind of AST (syntax tree) using standard python dictionaries
        # ATTN: can we use visitor/transform helper utilities from lark to do this all in a nicer way?

        # walk the parse tree and build out our itree hierarchy which organizes the parse tree by section -> child -> subchild
        # but all the BODY's of entries (and options) remained in parse tree form, just reorganized into our dictionary hierarchy
        # the main benefit at this point is all entries with IDs are sorted into their sections, so we can easily FIND an entry by its id

        # Note we need env here so that we can pass to convertTopLevelItemStoreAsChild for error handling

        # walk the children at root, which should be entries
        pchildren = parseTree.children
        for pchild in pchildren:
            self.convertTopLevelItemStoreAsChild(env, pchild)


    def convertTopLevelItemStoreAsChild(self, env, pnode):
        # top level can only be preliminary_matter, end_matter, or an entry
        # Note we need env here so that we can pass to convertEntryAddMergeChildAst
        rule = getParseNodeRuleNameSmart(pnode)
        if (rule == JrCbLarkRule_preliminary_matter):
            self.prelimaryMatter = self.convertGenericPnodeContents(pnode)
        elif (rule == JrCbLarkRule_end_matter):
            self.endMatter = self.convertGenericPnodeContents(pnode)
        elif (rule in [JrCbLarkRule_level1_entry, JrCbLarkRule_overview_level1_entry]):
            self.entries.convertEntryAddMergeChildAst(env, pnode, 1)
        else:
            # this shouldn't happen as parser should catch it
            raise makeJriException("Uncaught syntax error; expected top level item to be from {}.".format([JrCbLarkRule_preliminary_matter, JrCbLarkRule_end_matter, JrCbLarkRule_level1_entry, JrCbLarkRule_overview_level1_entry]), pnode)





    def taskRenderRun(self, env, task):
        # when "run" (interpretting) casebook code, functions may behave differently based on the TARGET OUTPUT
        # that is, we may be targetting latex, html, etc; and the FUNCTIONS may need to know that
        # we accomplish this with the use of some global variables/constants

        jrprint("Running task {}..".format(task.getTaskId()))
        #
        env.setTask(task)
        #
        # then call default run
        self.renderRun(task.getRmode(), env)


    def renderRun(self, rmode, env):
        # ROOT TREE RUN

        #task = env.getTask()

        # walk children ENTRIES and "run" each (they will store their output locally inside them)
        for child in self.entries.childList:
            if (child.calcIsSpecialEntryAlwaysRun()):
                # if its a special options or setup, then we always RUN it even if we are otherwise RENDERING
                child.renderRun(DefRmodeRun, env)
            else:
                child.renderRun(rmode, env)






















# entries (our main things)
class JrAstEntry(JrAst):
    def __init__(self, sloc, parentp, level):
        super().__init__(sloc, parentp)
        self.level = level
        #
        self.id = ""
        self.label = ""
        self.options = None
        self.bodyBlockSeqs = []
        #
        # options set
        self.autoId = None
        #
        self.entries = JrAstEntryChildHelper(self, self)


    def printDebug(self, depth):
        # nice hierarchical tabbed pretty print
        super().printDebug(depth, "LEVEL {}".format(self.level))
        astPrintDebugLine(depth+1, "ID: " + self.getId())
        astPrintDebugLine(depth+1, "LABEL: " + self.getLabel())
        if (self.options is not None):
            self.options.printDebug(depth+1)

        # blocks
        if (len(self.bodyBlockSeqs)>0):
            astPrintDebugLine(depth+1, "BLOCK SEQS ({}):".format(len(self.bodyBlockSeqs)))
            for blockseq in self.bodyBlockSeqs:
                blockseq.printDebug(depth+2)

        # children entries
        self.entries.printDebug(depth+1)



    def calcIsSpecialEntryAlwaysRun(self):
        # return True if we are a special options or setup entry
        if (self.id in DefSpecialEntryIdsAlwaysRun):
            return True
        return False


    def getDisplayIdLabel(self):
        return "{}:'{}'".format(self.getId(), self.getLabel())
    
    def getRuntimeDebugDisplay(self, env):
        return "ENTRY {}:{} (level {})".format(self.getId(), self.getLabel(), self.level)

    def setId(self, val):
        self.id = val
    def getId(self):
        return self.id

    def setLabel(self, val):
        self.label = val
    def getLabel(self):
        return self.label

    def setOptions(self, pnode):
        self.options = JrAstArgumentList(pnode, self)

    def setAutoId(self, val):
        self.autoId = val


    def addAstBodyBlockSeq(self, blockSeq):
        self.bodyBlockSeqs.append(blockSeq)

    def mergeNewBodyBlockSeqsFrom(self, otherEntry):
        for blockSeq in otherEntry.bodyBlockSeqs:
            self.addAstBodyBlockSeq(blockSeq)



    # helper function to get the ID of an entry node, which may be explicitly provided; we use label if no id
    def getEntryIdFallback(self, defaultVal):
        id = self.getId()
        if (jrfuncs.isNonEmptyString(id)):
            return id
        label = self.getLabel()
        if (jrfuncs.isNonEmptyString(label)):
            return label
        # defulat
        return defaultVal


    def convertCoreFromPnode(self, pnode):
        # Convery core from pnode to ast node, but NOT children (yet)
        # make sure we got what we expected
        verifyPNodeType(pnode, "adding entry children", [JrCbLarkRule_level1_entry, JrCbLarkRule_level2_entry, JrCbLarkRule_level3_entry, JrCbLarkRule_overview_level1_entry])

        # first two children of node are head and body
        pchildCount = len(pnode.children)
        if (pchildCount<2):
            raise makeJriException("Uncaught syntax error; expected first two children of parent entry to be header and body, but didn't find even these 2.", pnode)

        # head
        thisHeadPnode = pnode.children[0]
        verifyPNodeType(thisHeadPnode, "processing entry head", [JrCbLarkRule_entry_header])
        self.convertStoreHeaderInfo(thisHeadPnode)

        # body (may be None)
        thisBodyPnode = pnode.children[1]
        verifyPNodeType(thisBodyPnode, "processing entry body", [JrCbLarkRule_entry_body])
        self.convertAddBodyBlockSeq(thisBodyPnode)





    def convertStoreHeaderInfo(self, pnode):
        # process an entry header; this uses a parse tree grammar for specifying id, label, options
        for pchild in pnode.children:
            pchildValue = pchild.data.value
            if (pchildValue in [JrCbLarkRule_entry_id_opt_label, JrCbLarkRule_overview_level1_id]):
                for achild in pchild.children:
                    achildValue = achild.data.value
                    if (achildValue in [JrCbLarkRule_entry_id, JrCbLarkRule_overview_entry_id]):
                        self.setId(getParseTreeChildLiteralToken(achild))
                    elif (achildValue == JrCbLarkRule_entry_label):
                        self.setLabel(getParseTreeChildString(achild))
                    else:
                       raise makeJriException("Uncaught syntax error; expected to find {}.".format([JrCbLarkRule_entry_id, JrCbLarkRule_overview_entry_id, JrCbLarkRule_entry_label]), pchild)
            elif (pchildValue == JrCbLarkRule_entry_options):
                # options come as an argument list which is child 0 of options; nothing else
                optionsArgumentListNode = pchild.children[0]
                self.setOptions(optionsArgumentListNode)
            else:
                # this shouldnt happen because parser should flag it
                raise makeJriException("Uncaught syntax error; expected to find entry header element from {}.".format([JrCbLarkRule_entry_id_opt_label, JrCbLarkRule_overview_level1_id, JrCbLarkRule_entry_options]), pchild)


    def convertAddBodyBlockSeq(self, node):
        # just add the entire node as the body
        bodyContent = node.children[0]
        # find the block seq (may be None)
        if (bodyContent is not None):
            blockSeq = JrAstBlockSeq(bodyContent, self)
            self.addAstBodyBlockSeq(blockSeq)



    def applyOptions(self, env, optionsArgList):
        if (self.options is None):
            # no options to set -- but we would like to call on empty args for default
            optionsArgList = JrAstArgumentList(None, self)
        else:
            optionsArgList = self.options

        # we implement this by calling a special FUNCTION, and invoking it by passing argList, AND this entry as a special arg
        functionName = "_entryApplyOptions"
        # so this code looks much like the normal function execution
        funcVal = env.getEnvValue(self, functionName, None)
        if (funcVal is None):
            raise makeJriException("Internal error; could not find special entry options function '{}' in environment.".format(functionName), self)
        funcp = funcVal.getWrappedExpect(AstValFunction)

        # force pointer to us
        optionsArgList.setNamedArgValue("_entry", AstValObject(self.getSourceLoc(), self, self, False, True))

        # invoke it (alwaysin run mode)
        retv = funcp.invoke(DefRmodeRun, env, self, optionsArgList, [])

        # ignore return value
        return retv




    def renderRun(self, rmode, env):
        # Entry run
        # Entries are where we collect and store output -- their children blocks do not need to store output long term
        # an entry is made up of some BODIES (text inside it), and possible collection of CHILDREN ENTRIES
        # A level 1 entry is a SECTION (e.g. "Day1" or "Leads" or "Hints" or "Documents" or "Cover", etc.)
        # A level 2 entry is a LEAD
        # A level 3 entry might be a sub-lead
        #
        # ATTN: TODO we need to pass a self pointer into a local environment/context so that functions invoked from us can reference us

        jrprint("RenderRun ({}): {}".format(rmode, self.getRuntimeDebugDisplay(env)))

        # we wrap this childs renderrunning in a try catch exception in case we want to catch exceptions as warnings
        try:
            # Apply any options, which works by running an internal function on entry parameters passed
            self.applyOptions(env, self.options)

            # BODY of this entry
            for blockSeq in self.bodyBlockSeqs:
                blockSeq.renderRun(rmode, env)

        except Exception as e:
            context = env.getContext()
            if (context.getFlagContinueOnException()):
                context.displayException(e)
            else:
                raise e



        # CHILDREN ENTRIES (RECURSIVE CALL)
        for child in self.entries.childList:
            child.renderRun(rmode, env)
        






























class JrAstBlockSeq(JrAst):
    def __init__(self, blockSeqPnode, parentp):
        super().__init__(blockSeqPnode, parentp)
        #
        self.blocks = []
        #
        self.addBlocksFromBlockSeqPnode(blockSeqPnode)
    
    def printDebug(self, depth):
        # nice hierarchical tabbed pretty print
        super().printDebug(depth)
        # now our child blocks
        for block in self.blocks:
            block.printDebug(depth+1)



    def addBlocksFromBlockSeqPnode(self, blockSeqPnode):
        verifyPNodeType(blockSeqPnode, "block sequence", JrCbLarkRuleList_BlockSeqs)
        for pchild in blockSeqPnode.children:
            pchildData = pchild.data
            if (pchildData == JrCbLarkRule_Block_Newline):
                block = JrAstNewline(pchild, self)
            else:
                block = self.makeConvertDerivedBlock(pchild)
            self.blocks.append(block)


    
    def makeConvertDerivedBlock(self, blockpnode):
        # must be child
        blockpnode = blockpnode.children[0]
        rule = getParseNodeRuleNameSmart(blockpnode)
        if (rule == JrCbLarkRule_Block_Text):
            return JrAstBlockText(blockpnode, self)    
        elif (rule == JrCbLarkRule_Block_FunctionCall):
            return JrAstFunctionCall(blockpnode, self)
        elif (rule == JrCbLarkRule_Block_ControlStatement):
            return self.makeConvertControlStatement(blockpnode)
        elif (rule == JrCbLarkRule_Block_Expression):
            return JrAstExpression(blockpnode, self)  
        # not understood
        raise makeJriException("Internal rrror: Expected to process a block of type {} but got '{}'.".format([JrCbLarkRule_Block_FunctionCall, JrCbLarkRule_Block_Text, JrCbLarkRule_Block_ControlStatement, JrCbLarkRule_Block_Expression], rule), blockpnode)



    def makeConvertControlStatement(self, pnodeControlStatement):
        # make derived control statement
        pnode = pnodeControlStatement.children[0]
        rule = getParseNodeRuleNameSmart(pnode)
        if (rule == JrCbLarkRule_if_statement):
            return JrAstControlStatementIf(pnode, self)  
        elif (rule == JrCbLarkRule_for_statement):
            return JrAstControlStatementFor(pnode, self)  
        raise makeJriException("Internal error: Uknown control statement expected {} got '{}'.".format([JrCbLarkRule_if_statement,JrCbLarkRule_for_statement], rule), pnode)



    def renderRun(self, rmode, env):
        # Body render

        # render all the blocks in squence (note that a "block" could be various things, including a function call, a text block, etc.)
        for block in self.blocks:
            block.renderRun(rmode, env)



















































# fundamental building blocks

class JrAstBlockText(JrAst):
    def __init__(self, pnode, parentp):
        super().__init__(pnode, parentp)
        # ATTN: for now just store it
        self.blockPnode = pnode


    def renderRun(self, rmode, env):
        jrprint("Running ({}) BLOCKTEXT statement at {}".format(rmode, self.sloc.debugString()))
































class JrAstFunctionCall(JrAst):
    def __init__(self, pnode, parentp):
        super().__init__(pnode, parentp)
        #
        childCount = len(pnode.children)
        functionNameNode = pnode.children[0]
        argumentListNode = pnode.children[1]
        # now target brace groups
        if (childCount>3):
            raise makeJriException("Internal error: Expected 2 or 3 children for function call parse.", pnode)
        if (childCount==3):
            multiBraceGroupNode = pnode.children[2]
        else:
            multiBraceGroupNode = None
        #
        functionNameStr = functionNameNode.value
        self.functionName = functionNameStr
        self.argumentList = JrAstArgumentList(argumentListNode, self)
        if (multiBraceGroupNode is None):
            self.targetGroups = []
        else:
            self.targetGroups = convertParseMultiBraceGroupOrBlockSeq(multiBraceGroupNode, self)
        
        # ATTN:
        # note that at this point we have NOT evaluated/resolved the arguments or blocks -- they are simply stored as AST nodes -- uncomputed/unevaluated expressions that have no types, and could result in runtime errors, etc.,
        # they may in fact have recursive function calls inside the args, etc.
        # in fact we can't resolve them yet because we have no runtime environment/context


    def printDebug(self, depth):
        # nice hierarchical tabbed pretty print
        super().printDebug(depth, "{}(..)".format(self.getFunctionName()))


    def getRuntimeDebugDisplay(self, env):
        niceCallString = self.calcResolvedArgListWithDetailsForDebug(env)
        return "FUNCTION {}".format(niceCallString)


    def getFunctionName(self):
        return self.functionName


    def calcResolvedArgListWithDetailsForDebug(self, env):
        # to aid in debugging

        # get function pointer
        funcp = self.resolveFuncp(env)
        functionName = self.getFunctionName()

        # ask for the arg list
        compileTimeArgListString = self.argumentList.asDebugStr()
        annotatedArgListString = funcp.calcAnnotatedArgListStringForDebug(env, self, self.argumentList, self.targetGroups)
        return "{}({}) --> {}({})".format(functionName, compileTimeArgListString, functionName, annotatedArgListString)


    def resolveFuncp(self, env):
        # get function pointer
        functionName = self.getFunctionName()
        funcVal = env.getEnvValue(self, functionName, None)
        if (funcVal is None):
            raise makeJriException("Runtime error; Attemped to invoke undefined function: {}(..).".format(self.getFunctionName()), self)
        funcp = funcVal.getWrappedExpect(AstValFunction)
        return funcp


    def renderRun(self, rmode, env):
        #invoke the function
        try:
            funcRetVal = self.execute(rmode, env)
            funcRetAsString = funcRetVal.asNiceString(True)
            jrprint("run ({}) Functioncall {} returned {}".format(rmode, self.getRuntimeDebugDisplay(env), funcRetAsString))
        except Exception as e:
            context = env.getContext()
            if (context.getFlagContinueOnException()):
                context.displayException(e)
            else:
                raise e



    def execute(self, rmode, env):
        # execute the function, return an AstVal

        # get function pointer
        funcp = self.resolveFuncp(env)

        # invoke it
        retv = funcp.invoke(rmode, env, self, self.argumentList, self.targetGroups)

        # wrap return value
        funcRetVal = wrapValIfNotAlreadyWrapped(self, self, retv)

        return funcRetVal







































class JrAstControlStatementIf(JrAst):
    def __init__(self, pnode, parentp):
        super().__init__(pnode, parentp)
        #
        expressionNode = pnode.children[0]
        self.ifExpression = JrAstExpression(expressionNode, self)
        self.consequenceTrue = None
        self.elseIf = None
        self.consequenceElse = None
        consequenceNode = pnode.children[1]
        self.convertConsequenceSet(consequenceNode)
        pass

    def convertConsequenceSet(self, consequenceSetNode):
        # set other parts of if
        verifyPNodeType(consequenceSetNode, "if_consequence", [JrCbLarkRule_if_consequence])
        consequenceChildNode = consequenceSetNode.children[0]
        self.consequenceTrue = convertParseBraceGroupOrBlockSeq(consequenceChildNode, self)
        # now if there is ANOTHER child it is EITHER an elif or an else
        childCount = len(consequenceSetNode.children)
        if (childCount>1):
            elseChildNode = consequenceSetNode.children[1]
            rule = getParseNodeRuleNameSmart(elseChildNode)
            if (rule == JrCbLarkRule_elif_statement):
                elseIfChildNode = elseChildNode.children[0]
                self.elseIf = JrAstControlStatementIf(elseIfChildNode, self)
            elif (rule == JrCbLarkRule_else_statement):
                elseConsquenceNode = elseChildNode.children[0]
                self.consequenceElse = convertParseBraceGroupOrBlockSeq(elseConsquenceNode, self)
            else:
                raise makeAstExceptionPNodeType("if consequence set", elseChildNode, [JrCbLarkRule_elif_statement, JrCbLarkRule_else_statement])
        

    def renderRun(self, rmode, env):
        jrprint("run IF statement")

        consequenceResult = None

        # evaluate expression
        expressionResultVal = self.ifExpression.resolve(env, True)
        # is it true?
        evaluatesTrue = expressionResultVal.getWrappedExpect(AstValBool)
        if (evaluatesTrue):
            # run the consequence
            consequenceResult = self.consequenceTrue.renderRun(rmode, env)
        else:
            # at most one if these can be non-None (possibly both)
            if (self.elseIf is not None):
                # we have an else if IF
                consequenceResult = self.elseIf.renderRun(rmode, env)
            elif (self.consequenceElse is not None):
                consequenceResult = self.self.consequenceElse.renderRun(rmode, env)
            else:
                # nothing to do
                pass

        # ATTN: unfinished; return consequenceResult
        pass




















class JrAstControlStatementFor(JrAst):
    def __init__(self, pnode, parentp):
        super().__init__(pnode, parentp)
        #
        forExpressionNode = pnode.children[0]
        verifyPNodeType(forExpressionNode, "for expression", [JrCbLarkRule_for_expression_in])
        # identifier that will loop through list
        identifierNameNode = forExpressionNode.children[0]
        self.identifierName = getParseNodeTokenValue(identifierNameNode)
        # expression which will HAVE to evaluate at runtime into a list
        expressionNode = forExpressionNode.children[1]
        self.inExpression = JrAstExpression(expressionNode, self)
        # consequence loop
        consequenceNode = pnode.children[1]
        self.loopConsequence = convertParseBraceGroupOrBlockSeq(consequenceNode, self)


    def renderRun(self, rmode, env):
        jrprint("RenderRun ({}) FOR statement - ATTN: UNFINISHED".format(rmode))













































# JrAstArgumentList represents two lists of arguments being passed to a function, a positional and named list
# note that this is a JrAst derived class, meaning that it is not a general utility class but rather a node created from parse tree (ie an argument list found in the source parse)
class JrAstArgumentList(JrAst):
    def __init__(self, pnode, parentp):
        super().__init__(pnode, parentp)
        #
        self.positionalArgs = []
        self.namedArgs = {}
        #
        if (pnode is not None):
            verifyPNodeType(pnode, "parsing argument list", [JrCbLarkRule_argument_list])
            # walk children
            for childpnode in pnode.children:
                verifyPNodeType(childpnode, "parsing argument child list", [JrCbLarkRule_positional_argument_list, JrCbLarkRule_named_argument_list])
                childData = childpnode.data
                if (childData == JrCbLarkRule_positional_argument_list):
                    self.positionalArgs = convertPositionalArgList(childpnode, self)
                elif (childData == JrCbLarkRule_named_argument_list):
                    self.namedArgs = convertNamedArgList(childpnode, self)


    def asDebugStr(self):
        parts = []
        for arg in self.positionalArgs:
            simpleArgStr = arg.asDebugStr()
            parts.append(simpleArgStr)
        for key,arg in self.namedArgs.items():
            simpleArgStr = "{}={}".format(key, arg.asDebugStr())
            parts.append(simpleArgStr)
        niceString = ", ".join(parts)
        return niceString


    def getPositionArgs(self):
        return self.positionalArgs
    def getNamedArgs(self):
        return self.namedArgs

    def setNamedArgValue(self, argName, value):
        self.namedArgs[argName] = value



























class JrAstNewline(JrAst):
    def __init__(self, pnode, parentp):
        super().__init__(pnode, parentp)
        # nothing else to do here, it's just a newline that may be significant for text production


    def renderRun(self, rmode, env):
        jrprint("RenderRun ({}) NEWLINE statement".format(rmode))



















# brace group is just like a block sequence
# currently we just handle the functionality in base blockSeq class
class JrAstBraceGroup(JrAstBlockSeq):
    def __init__(self, pnode, parentp):
        super().__init__(pnode, parentp)










































# expressions, simple or complext
# this will require quite a bit of work
# but i think rules are always going to be 1 or 2 children
# ATTN: unfinished
# JrAstExpression currently just wraps a specific operation/atom
class JrAstExpression(JrAst):
    def __init__(self, pnode, parentp):
        super().__init__(pnode, parentp)
        #
        self.element = convertExpression(pnode, self)


    def asDebugStr(self):
        # IF the expression is JUST a wrapped value, return that
        atomicVal = self.getAstValOrNoneIfComplex()
        if (atomicVal is not None):
            return atomicVal.asDebugStr()
        # fallback to just reportign class
        return "CompoundExpression"

    def getAstValOrNoneIfComplex(self):
        # return the astAval if its a simple expression
        element = self.element
        if (isinstance(element, AstVal)):
            return element
        # atomic expressions is same thing, a single value wrapped
        if (isinstance(element, JrAstExpressionAtom)):
            operand = self.element.getOperand()
            return operand
        return None


    def resolve(self, env, flagResolveIdentifiers):
        # resolve the expression (recursively using ast)
        return self.element.resolve(env, flagResolveIdentifiers)


    def renderRun(self, rmode, env):
        jrprint("RenderRun ({}) EXPRESSION".format(rmode))







class JrAstExpressionBinary(JrAst):
    def __init__(self, rule, pnode, parentp):
        super().__init__(pnode, parentp)
        #
        self.rule = rule
        self.leftOperand = convertExpressionOperand(pnode.children[0], self)
        self.rightOperand = convertExpressionOperand(pnode.children[1], self)

    def resolve(self, env, flagResolveIdentifiers):
        # resolve the expression (recursively using ast)
        # run the operation on the resolved operand
        # resolve operand
        leftOperandResolved = self.leftOperand.resolve(env, flagResolveIdentifiers)
        rightOperandResolved = self.rightOperand.resolve(env, flagResolveIdentifiers)
        rule = self.rule
        #
        if (rule == JrCbLarkRule_Operation_Binary_add):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, (lambda a,b: a+b), (lambda a,b: a+b), None)
        elif (rule == JrCbLarkRule_Operation_Binary_sub):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, (lambda a,b: a-b), None, None)
        elif (rule == JrCbLarkRule_Operation_Binary_or):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, None, None, (lambda a,b: (a or b)))
        elif (rule == JrCbLarkRule_Operation_Binary_and):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, None, None, (lambda a,b: (a and b)))
        elif (rule == JrCbLarkRule_Operation_Binary_mul):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, (lambda a,b: a*b), (lambda a,b: a*b), None)
        elif (rule == JrCbLarkRule_Operation_Binary_div):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, (lambda a,b: a/b), None, None)
        elif (rule == JrCbLarkRule_Operation_Binary_lessthan):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, None, None, (lambda a,b: (a < b)))
        elif (rule == JrCbLarkRule_Operation_Binary_lessthanequal):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, None, None, (lambda a,b: (a <= b)))
        elif (rule == JrCbLarkRule_Operation_Binary_greaterthan):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, None, None, (lambda a,b: (a > b)))
        elif (rule == JrCbLarkRule_Operation_Binary_greaterthanequal):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, None, None, (lambda a,b: (a >= b)))
        elif (rule == JrCbLarkRule_Operation_Binary_equal):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, (lambda a,b: (a == b)), (lambda a,b: (a == b)), (lambda a,b: (a == b)))
        elif (rule == JrCbLarkRule_Operation_Binary_notequal):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, (lambda a,b: (a != b)), (lambda a,b: (a != b)), (lambda a,b: (a != b)))
        elif (rule == JrCbLarkRule_Operation_Binary_in):
            [success, operationResult] = self.operateBinaryInCollection(rule, leftOperandResolved, rightOperandResolved)
        else:
            raise makeJriException("Internal error: unknown binary expression operator ().".format(rule), self)
        if (not success):
            raise self.makeExpExceptionUnsupportedOperands(self, rule, leftOperandResolved, rightOperandResolved)
        return operationResult


    # helper function for running numeric/string/bool lambda binary operations based on the value types with generic errors for mismatched operands, etc.
    def operateBinary(self, opLabel, leftOperand, rightOperand, numericOp, stringOp, boolOp):
        leftType = leftOperand.getType()
        rightType = rightOperand.getType()
        leftOperandValue = leftOperand.getWrapped()
        rightOperandValue = rightOperand.getWrapped()
        #
        success = False
        operationResult = None
        #
        if (leftType != rightType):
            raise self.makeExpExceptionOperandMismatch(self, opLabel, leftOperand, rightOperand)
        #
        if (leftType == AstValNumber) and (numericOp is not None):
            resultVal = numericOp(leftOperandValue, rightOperandValue)
            operationResult = AstValNumber(self, self, resultVal)
            success = True
        if (leftType == AstValString) and (stringOp is not None):
            resultVal = stringOp(leftOperandValue, rightOperandValue)
            operationResult = AstValString(self, self, resultVal)
            success = True
        if (leftType == AstValBool) and (boolOp is not None):
            resultVal = boolOp(leftOperandValue, rightOperandValue)
            operationResult = AstValBool(self, self, resultVal)
            success = True
        return [success, operationResult]



    def operateBinaryInCollection(self, operationLabel, leftOperand, rightOperand):
        leftType = leftOperand.getType()
        rightType = rightOperand.getType()
        #
        success = False
        operationResult = None
        #
        try:
            # we will try to do native python IN test; if we throw PYTHON exception we will convert it to our own
            if (rightType == AstValList):
                resultVal = leftOperand in rightOperand
                success = True
            elif (rightType == AstValDict):
                resultVal = leftOperand in rightOperand
                success = True
            if (success):
                operationResult = AstValBool(self, self, resultVal)
        except Exception as e:
            # failed
            success = False
            detailStr = self.makeOperandDebugString(operationLabel, leftOperand, rightOperand)
            raise makeJriException("Runtime error: incompatible operation expression types for: {}.".format(detailStr), self)
        #
        return [success, operationResult]


    def makeOperandDebugString(self, operationLabel, leftOperand, rightOperand):
        leftTypeStr = calcNiceShortTypeStr(leftOperand)
        rightTypeStr = calcNiceShortTypeStr(rightOperand)
        msg = "'{}:{}' *{}* '{}:{}'".format(leftTypeStr, leftOperand.getWrappedForDisplay(), operationLabel, rightTypeStr, rightOperand.getWrappedForDisplay())
        return msg





    def makeExpExceptionOperandMismatch(self, sloc, operationLabel, leftOperand, rightOperand):
        detailStr = self.makeOperandDebugString(operationLabel, leftOperand, rightOperand)
        return makeJriException("Runtime error: mismatch of operation operands: {}.".format(detailStr), sloc)

    def makeExpExceptionUnsupportedOperands(self, sloc, operationRuleLabel, leftOperand, rightOperand):
        detailStr = self.makeOperandDebugString(operationRuleLabel, leftOperand, rightOperand)
        return makeJriException("Runtime error: Unsupported operation operands for: {}.".format(detailStr), sloc)
















class JrAstExpressionUnary(JrAst):
    def __init__(self, rule, pnode, parentp):
        super().__init__(pnode, parentp)
        #
        self.rule = rule
        self.operand = convertExpressionOperand(pnode.children[0], self)

    def resolve(self, env, flagResolveIdentifiers):
        # resolve the expression (recursively using ast)
        # run the operation on the resolved operand
        # resolve operand
        operandResolved = self.operand.resolve(env, flagResolveIdentifiers)
        # run operation
        if (self.rule == JrCbLarkRule_Operation_Unary_neg):
            operationResult = self.operateNeg(operandResolved)
        elif (self.rule == JrCbLarkRule_Operation_Unary_not):
            operationResult = self.operateNot(operandResolved)
        else:
            raise makeJriException("Internal error: unknown unary expression operator ().".format(self.rule), self)
        # return result
        return operationResult
    
    def operateNeg(self, operand):
        operandAsNumber = operand.getWrappedExpect(AstValNumber)
        resultVal = -1 * operandAsNumber
        # recast to numeric val
        operationResult = AstValNumber(self, self, resultVal)
        return operationResult

    def operateNot(self, operand):
        operandAsBool = operand.getWrappedExpect(AstValBool)
        resultVal = (not operandAsBool)
        # recast to bool val
        operationResult = AstValBool(self, self, resultVal)
        return operationResult





class JrAstExpressionAtom(JrAst):
    def __init__(self, rule, pnode, parentp):
        super().__init__(pnode, parentp)
        #
        self.rule = rule
        operandNode = pnode.children[0]
        if (rule == JrCbLarkRule_Atom_string):
            self.operand = AstValString(pnode, self, getParseTreeString(pnode))
        elif (rule == JrCbLarkRule_Atom_number):
            self.operand = AstValNumber(pnode, self, getParseNodeTokenValue(operandNode))
        elif (rule == JrCbLarkRule_Atom_boolean):
            self.operand = AstValBool(pnode, self, getParseNodeBool(operandNode))
        elif (rule == JrCbLarkRule_Atom_identifier):
            self.operand = AstValIdentifier(pnode, self, getParseNodeTokenValue(operandNode))
        elif (rule == JrCbLarkRule_Atom_null):
            self.operand = AstValNull(pnode, self)
        else:
            raise makeJriException("Internal error; unexpected token in atom expression ({}).".format(rule), pnode)

    def resolve(self, env, flagResolveIdentifiers):
        # resolve the expression (recursively using ast)
        # for an atom value, we just ask the value to resolve
        operandResolved = self.operand.resolve(env, flagResolveIdentifiers)
        return operandResolved

    def getOperand(self):
        return self.operand





class JrAstExpressionCollectionList(JrAst):
    def __init__(self, pnode, parentp):
        super().__init__(pnode, parentp)
        #
        collectionNode = pnode.children[0]
        if (collectionNode is None):
            itemList = []
        else:
            itemList = convertPositionalArgList(collectionNode, self)
        #
        self.itemList = itemList


    def resolve(self, env, flagResolveIdentifiers):
        # resolve the expression (recursively using ast)

        # for a list, we need to ask each item in list to resolve
        resolvedItemList = []
        for item in self.itemList:
            resolvedItemList.append(item.resolve(env, flagResolveIdentifiers))
        return AstValList(self, self, resolvedItemList)





class JrAstExpressionCollectionDict(JrAst):
    def __init__(self, pnode, parentp):
        super().__init__(pnode, parentp)
        #
        collectionNode = pnode.children[0]
        if (collectionNode is None):
            itemDict = {}
        else:
            itemDict = convertDictionary(collectionNode, self)
        #
        self.itemDict = itemDict



    def resolve(self, env, flagResolveIdentifiers):
        # resolve the expression (recursively using ast)

        # for a dict, we need to ask each item in dict to resolve
        resolvedItemDict = {}
        for key, item in self.itemDict.items():
            resolvedItemDict[key] = item.resolve(env, flagResolveIdentifiers)
        return AstValDict(self, self, resolvedItemDict)


















































# entry child helper manages the children of an entry
class JrAstEntryChildHelper(JrAst):
    def __init__(self, sloc, parentp):
        super().__init__(sloc, parentp)
        # ordered list of children
        self.childList = []
        # hash of children by Id
        self.childIdHash = {}

    def printDebug(self, depth):
        # nice hierarchical tabbed pretty print
        str = None
        childCount = len(self.childList)
        if (childCount==0):
            #str = "Zero children"
            pass
        elif (childCount==1):
            str = "1 child:"
        else:
            str = "{} children:".format(childCount)
        #
        if (str is not None):
            super().printDebug(depth, str)
            #astPrintDebugLine(depth, "{}: {} @ {}".format(self.getTypeStr(), str, self.getOwnerParentp().sloc.debugString()))

        # now children
        for child in self.childList:
            child.printDebug(depth+1)


    def getOwnerParentp(self):
        return self.parentp


    def findExistingEntryChild(self, entryAst):
        # return info on an existing child or NONE if none matches
        if (self.childIdHash is None):
            return None
        entryId = entryAst.getEntryIdFallback(JrCb_blankEntryId)
        if (entryId in self.childIdHash):
            return self.childIdHash[entryId]
        return None


    def addChild(self, env, childAst, pnode):
        # create children if there are none yet
        if (self.childList is None):
            self.childList = []
            self.childIdHash = {}

        # add to hash
        entryId = childAst.getEntryIdFallback(JrCb_blankEntryId)
        # now, does this ID already exist? (if its blank no id, then dont even bothers)
        if (entryId!=JrCb_blankEntryId) and (entryId in self.childIdHash):
            # it already exists! i dont think this branch should ever take place, since caller checks for this and tries to merge INSTEAD of calling this
            raise makeJriException("Internal grammar error: Asked to add child item with a duplicate id that is already a child of parent ({}).".format(entryId), pnode)
        else:
            # add it
            childIndex = len(self.childList)
            self.childList.append(childAst)   
            # add hash if it has an id; note that check above should prevent it from ever overwriting/clashing
            if (entryId != JrCb_blankEntryId):
                self.childIdHash[entryId] = childAst



    def convertEntryAddMergeChildAst(self, env, pnode, expectedLevel):
        # start by creating a NEW JrAstEntry node (we may dispose it if we choose to merge but it's more straighforward to do this)
        # NOTE: we pass env here so that we can catch exceptions at this level and continue if we want for better error reporting

        try:
            return self.convertEntryAddMergeChildAstDoWork(env, pnode, expectedLevel)
        except Exception as e:
            context = env.getContext()
            if (context.getFlagContinueOnException()):
                context.displayException(e)
            else:
                raise e


    def convertEntryAddMergeChildAstDoWork(self, env, pnode, expectedLevel):
        newEntryAst = JrAstEntry(pnode, self.getOwnerParentp(), expectedLevel)
        # convert core but not children
        newEntryAst.convertCoreFromPnode(pnode)

        # now see if this exists already as a child and should be merged
        existingChild = self.findExistingEntryChild(newEntryAst)

        if (existingChild is None):
            # no existing child, so we will add this child, and add its children recursively to it
            self.addChild(env, newEntryAst, pnode)
            recurseEntryAst = newEntryAst
        else:
            # we have an existing child with this id, so we will merge children into it, AFTER we check for conflicts
            recurseEntryAst = existingChild
            # check for conflict
            if (jrfuncs.isNonEmptyString(newEntryAst.getLabel())):
                # want to use new label
                if (jrfuncs.isNonEmptyString(existingChild.getLabel()) and (existingChild.getLabel() != newEntryAst.getLabel())):
                    raise makeJriException("Grammar error: Redefinition of label in repeat use of entry header for entry with id '{}' (only one should be non-empty); old={} vs new={}.".format(newEntryAst.getDisplayIdLabel(), existingChild.getLabel(), newEntryAst.getLabel()), pnode)
                existingChild.label = newEntryAst.label
            if (newEntryAst.options is not None):
                # want to use new options
                if (existingChild.options is not None) and (existingChild.options != newEntryAst.options):
                    raise makeJriException("Grammar error: Redefinition of options in repeat use of entry header for entry with id '{}' (only one should be non-empty); old={} vs new={}.".format(newEntryAst.getDisplayIdLabel(), existingChild.options, newEntryAst.options), pnode)
                existingChild.options = newEntryAst.options
            # is body trickier? do we want to merge?
            if (len(newEntryAst.bodyBlockSeqs) > 0):
                # new bodies to add
                # we could complain about both having bodies, but instead we just append bodies -- but WHY?
                if (len(existingChild.bodyBlockSeqs)>0):
                    if (False):
                        raise makeJriException("Grammar error: Redefinition of body in repeat use of entry header for entry with id '{}' (only one should be non-empty); old={} vs new={}.".format(newEntryAst.getDisplayIdLabel(), existingChild.body, newEntryAst.body), pnode)
                # APPEND body from new to existing
                # ATTN: What is the use case for this? THE USE CASE IS SECTIONS LIKE SETUP|OPTIONS
                existingChild.mergeNewBodyBlockSeqsFrom(newEntryAst)


        # now recurse and add OUR children (those after head and body), to the newly added child ast OR the merged existing one
        pchildCount = len(pnode.children)
        if (pchildCount>2):
            for i in range(2, pchildCount):
                pchild = pnode.children[i]
                recurseEntryAst.entries.convertEntryAddMergeChildAst(env, pchild, expectedLevel+1)





