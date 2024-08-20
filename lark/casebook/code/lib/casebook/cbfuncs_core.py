# casebook functions


# jr ast helpers
from .jrcbfuncs import CbFunc, CbParam
from .jrast import AstValString, AstValNumber, AstValBool, AstValIdentifier, AstValList, AstValDict, AstValObject
from .jrastvals import makeAstValNull
from .jrastutilclasses import DefRmodeRun, DefRmodeRender
from .jriexception import *






def buildFunctionList():
    # create the functions
    functionList = []

    # special internal function invoked on setting options
    functionList.append(CbFunc("_entryApplyOptions", "Internal function for applying options to entry", [
            CbParam("_entry", "Object pointer to entry whose options are being set", None, None, False),
            CbParam("autoid", "Automatically assign a lead id", False, AstValBool, True),
            CbParam("special", "Is this a special entry?", False, AstValBool, True),
            CbParam("sortindex", "Sort index", -1, AstValNumber, True),
            CbParam("childSort", "Sort order for children", "", ["", "alpha", "index"], True),
            CbParam("layoutStyle", "Style for layout of entry", "", ["", "cover", "oneColumn", "solo", "twoColumn"], True),
            CbParam("tombstones", "Should we show tombstombs between child entries", True, AstValBool, True),
            CbParam("labelcontd", "Add label saying 'continued from'", "", AstValString, True),
            CbParam("time", "Time clicks", 1, AstValNumber, True),
            CbParam("deadline", "Deadline day for a check", -1, AstValNumber, True),
        ],
        None, None,
        funcApplyEntryOptions
        ))


    functionList.append(CbFunc("declareVar", "Declarts a variable", [
            CbParam("var", "The variable name to set", None, AstValIdentifier, False),
            CbParam("val", "Initial value for the variable", makeAstValNull(), None, True),
            CbParam("desc", "Description", "", None, True),
        ],
        None, None,
        funcDeclareVar
        ))
    functionList.append(CbFunc("declareConst", "Declarts a variable", [
            CbParam("var", "The variable name to set", None, AstValIdentifier, False),
            CbParam("val", "Initial value for the variable", None, None, True),
            CbParam("desc", "Description", "", None, True),
        ],
        None, None,
        funcDeclareConst
        ))

    functionList.append(CbFunc("set", "Sets a variable to a value", [
            CbParam("var", "The variable name to set", None, AstValIdentifier, False),
            CbParam("val", "The new value for the variable", None, None, True),
        ],
        None, None,
        funcSet
        ))

    functionList.append(CbFunc("defineTag", "Defines a tag", [
            CbParam("tagId", "The dotted identifier used to refer to the tag", None, AstValString, True),
        ],
        None, None,
        funcDefineTag
        ))


    # maybe we will rework these
    functionList.append(CbFunc("blurbCoverPage", "Creates a cover page blurb", [
        ],
        "text", 1,
        funcBlurbCoverPage
        ))


    functionList.append(CbFunc("image", "Insert an image", [
            CbParam("path", "Relative path to file image", None, AstValString, True),
            CbParam("height", "Height (e.g. 3in)", "", AstValString, True),
        ],
        "text", None,
        funcImage
        ))

    functionList.append(CbFunc("include", "Include a file in output", [
            CbParam("path", "Relative path to file to insert", None, AstValString, True),
        ],
        "text", None,
        funcUnimplementedUnified
        ))

    functionList.append(CbFunc("leadid", "Add reference to a lead", [
            CbParam("id", "ID of lead", None, AstValString, True),
        ],
        "text", None,
        funcUnimplementedUnified
        ))

    functionList.append(CbFunc("golead", "Add text to go to lead", [
            CbParam("id", "ID of lead", None, AstValString, True),
            CbParam("link", "Text link", "", AstValString, True),
        ],
        "text", None,
        funcUnimplemented
        ))
    functionList.append(CbFunc("returnlead", "Add text to go to lead", [
            CbParam("id", "ID of lead", None, AstValString, True),
            CbParam("link", "Text link", "", AstValString, True),
        ],
        "text", None,
        funcUnimplemented
        ))
    functionList.append(CbFunc("reflead", "Add text to refer to lead", [
            CbParam("id", "ID of lead", None, AstValString, True),
        ],
        "text", None,
        funcUnimplementedUnified
        ))


    functionList.append(CbFunc("gaintag", "Mark a tag", [
            CbParam("id", "ID of tag", None, AstValString, True),
            CbParam("define", "Should the tag be defined if it doesn't exist?", False, AstValBool, True),
        ],
        "text", None,
        funcUnimplemented
        ))
    
    functionList.append(CbFunc("hastag", "Check if user has tag", [
            CbParam("id", "ID of tag", None, AstValString, True),
            CbParam("time", "how many clicks", 0, AstValNumber, True),
        ],
        "text", None,
        funcUnimplemented
        ))

    functionList.append(CbFunc("requiretag", "Put the target block in a new lead and only let them go there if they have tag", [
            CbParam("id", "ID of tag", None, AstValString, True),
            CbParam("time", "how many clicks", 0, AstValNumber, True),
        ],
        "text", 1,
        funcUnimplemented
        ))

    functionList.append(CbFunc("missingtag", "Is player missing a tag", [
            CbParam("id", "ID of tag", None, AstValString, True),
        ],
        "text", None,
        funcUnimplemented
        ))
    
    functionList.append(CbFunc("mentiontags", "Is player missing a tag", [
            CbParam("tags", "list of tags", [], AstValList, True),
        ],
        "text", None,
        funcUnimplementedUnified
        ))


    functionList.append(CbFunc("dictfunc", "test", [
            CbParam("adict", "test dictionary", [], AstValDict, True),
        ],
        "text", None,
        funcUnimplemented
        ))



    functionList.append(CbFunc("deadlineinfo", "Insert deadline info", [
            CbParam("day", "description n/a", None, AstValNumber, True),
            CbParam("section", "description n/a", None, AstValString, True),
            CbParam("time", "description n/a", None, AstValNumber, True),
            CbParam("start", "description n/a", None, AstValNumber, True),
            CbParam("end", "description n/a", None, AstValNumber, True),
            CbParam("last", "description n/a", False, AstValBool, True),
        ],
        "text", None,
        funcUnimplementedUnified
        ))

    functionList.append(CbFunc("remind", "Insert reminder", [
            CbParam("type", "Reminder type", None, AstValString, True),
        ],
        "text", None,
        funcUnimplementedUnified
        ))

    functionList.append(CbFunc("stop", "Insert stop text", [
            CbParam("type", "Stop type", None, AstValString, True),
        ],
        "text", None,
        funcUnimplementedUnified
        ))

    functionList.append(CbFunc("symbol", "Insert symbol (unicode/icon) text", [
            CbParam("id", "Symbol id", None, AstValString, True),
        ],
        "text", None,
        funcUnimplementedUnified
        ))

    functionList.append(CbFunc("mark", "Mark checkboxes", [
            CbParam("type", "Mark type", None, AstValString, True),
            CbParam("count", "How many to mark", 1, AstValNumber, True),
        ],
        "text", None,
        funcUnimplemented
        ))

    functionList.append(CbFunc("format", "Format text", [
            CbParam("style", "style type", None, AstValString, True),
        ],
        "text", 1,
        funcUnimplementedUnified
        ))


    functionList.append(CbFunc("radio", "Format for radio", [
        ],
        "text", 1,
        funcUnimplementedUnified
        ))
    
    functionList.append(CbFunc("box", "Format in box", [
        ],
        "text", 1,
        funcUnimplementedUnified
        ))

    functionList.append(CbFunc("logicsuggests", "Add mindmap node", [
            CbParam("id", "Lead id", None, AstValString, True),
            CbParam("link", "Link label", "", AstValString, True),
        ],
        "text", None,
        funcUnimplementedUnified
        ))
    functionList.append(CbFunc("logicsuggestedby", "Add mindmap node", [
            CbParam("id", "Lead id", None, AstValString, True),
            CbParam("link", "Link label", "", AstValString, True),
        ],
        "text", None,
        funcUnimplementedUnified
        ))
    functionList.append(CbFunc("logicimplies", "Add mindmap node", [
            CbParam("id", "Lead id", None, AstValString, True),
            CbParam("link", "Link label", "", AstValString, True),
        ],
        "text", None,
        funcUnimplementedUnified
        ))
    functionList.append(CbFunc("logicimpliedby", "Add mindmap node", [
            CbParam("id", "Lead id", None, AstValString, True),
            CbParam("link", "Link label", "", AstValString, True),
        ],
        "text", None,
        funcUnimplementedUnified
        ))
    functionList.append(CbFunc("logicirrelevant", "Add mindmap node", [
            CbParam("id", "Lead id", "", AstValString, True),
            CbParam("link", "Link label", "", AstValString, True),
        ],
        "text", None,
        funcUnimplementedUnified
        ))


    functionList.append(CbFunc("inlineback", "Create inline", [
            CbParam("link", "Text link", "", AstValString, True),
            CbParam("time", "Time clicks", 0, AstValNumber, True),
        ],
        "text", 1,
        funcUnimplemented
        ))
    functionList.append(CbFunc("inline", "Create inline", [
            CbParam("link", "Text link", "", AstValString, True),
            CbParam("time", "Time clicks", 0, AstValNumber, True),
            CbParam("demerits", "Demerit checkboxes", 0, AstValNumber, True),
            CbParam("unless", "Unless text", "", AstValString, True),
        ],
        "text", 1,
        funcUnimplemented
        ))
    functionList.append(CbFunc("inlinehint", "Create inline", [
            CbParam("link", "Text link", "", AstValString, True),
            CbParam("time", "Time clicks", 0, AstValNumber, True),
            CbParam("demerits", "Demerit checkboxes", 2, AstValNumber, True),
        ],
        "text", 1,
        funcUnimplemented
        ))


    functionList.append(CbFunc("time", "Instruct player to advance clock by some clicks", [
            CbParam("count", "How many clicks", 1, AstValNumber, True),
        ],
        "text", None,
        funcUnimplemented
        ))

    functionList.append(CbFunc("beforeday", "Text saying if before day", [
            CbParam("day", "Day number", None, AstValNumber, True),
        ],
        "text", None,
        funcUnimplemented
        ))
    functionList.append(CbFunc("afterday", "Text saying if after day", [
            CbParam("day", "Day number", None, AstValNumber, True),
        ],
        "text", None,
        funcUnimplemented
        ))
    functionList.append(CbFunc("onday", "Text saying if on day", [
            CbParam("day", "Day number", None, AstValNumber, True),
        ],
        "text", None,
        funcUnimplemented
        ))

    functionList.append(CbFunc("otherwise", "Text saying otherwise", [
        ],
        "text", None,
        funcUnimplemented
        ))


    functionList.append(CbFunc("form", "Form field insert", [
            CbParam("type", "Form field type", None, AstValString, True),
        ],
        "text", None,
        funcUnimplementedUnified
        ))

    functionList.append(CbFunc("separator", "separator insert", [
            CbParam("type", "Separator type", None, AstValString, True),
        ],
        "text", None,
        funcUnimplementedUnified
        ))


    functionList.append(CbFunc("copynext", "instruction to copy body from next entry", [
        ],
        None, None,
        funcUnimplementedUnified
        ))

    functionList.append(CbFunc("autohint", "generate an autohint", [
        ],
        None, None,
        funcUnimplementedUnified
        ))


    functionList.append(CbFunc("print", "print value", [
            CbParam("expression", "Expression to print", None, None, True),
        ],
        "text", None,
        funcUnimplemented
        ))


    return functionList























































# FUNCTION IMPLEMENTATIONS

def funcApplyEntryOptions(rmode, env, astloc, args, targets):
    # apply options to entry
    entry = args["_entry"].getWrappedExpect(AstValObject)
    if (rmode == DefRmodeRun):
        entry.setAutoId(args["autoid"].getWrappedExpect(AstValBool))
    else:
        raise makeJriException("In function funcApplyEntryOptions but in rmode!= run; do not know what to do.", astloc)



def funcDeclareVar(rmode, env, astloc, args, targets):
    varName = args["var"].getWrappedExpect(AstValIdentifier)
    description = args["desc"].getWrappedExpect(AstValString)
    value = args["val"]
    #
    if (rmode == DefRmodeRun):
        env.declareEnvVar(astloc, varName, description, value, False)
    else:
        raise makeJriException("In function funcDeclareVar but in rmode!= run; do not know what to do.", astloc)


def funcDeclareConst(rmode, env, astloc, args, targets):
    varName = args["var"].getWrappedExpect(AstValIdentifier)
    description = args["desc"].getWrappedExpect(AstValString)
    value = args["val"]
    #
    if (rmode == DefRmodeRun):
        env.declareEnvVar(astloc, varName, description, value, True)
    else:
        raise makeJriException("In function funcDeclareConst but in rmode!= run; do not know what to do.", astloc)


def funcSet(rmode, env, astloc, args, targets):
    varName = args["var"].getWrappedExpect(AstValIdentifier)
    value = args["val"]
    #
    if (rmode == DefRmodeRun):
        env.setEnvValue(astloc, varName, value, True)
    else:
        raise makeJriException("In function funcSet but in rmode!= run; do not know what to do.", astloc)


def funcDefineTag(rmode, env, astloc, args, targets):
    tagId = args["tagId"].getWrappedExpect(AstValString)
    # ATTN: unfinished
    if (rmode == DefRmodeRun):
        pass
    else:
        raise makeJriException("In function funcDefineTag but in rmode!= run; do not know what to do.", astloc)







#




def funcBlurbCoverPage(rmode, env, astloc, args, targets):
    return "BLURB COVER PAGE TODO"



def funcImage(rmode, env, astloc, args, targets):
    return "IMAGE INSERT TODO"



def funcUnimplemented(rmode, env, astloc, args, targets):
    if (rmode == DefRmodeRun):
        return "Unimplemented function output"
    else:
        return "Unimplemented function output (WARNING THIS FUNCTION IS NOT EXPECTED TO RUN IN '{}' mode)".format(rmode)
        raise makeJriException("In function funcUnimplemented but in rmode!= run; do not know what to do.", astloc)


def funcUnimplementedUnified(rmode, env, astloc, args, targets):
    return "Unimplemented unified run/render function output"
