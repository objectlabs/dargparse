###############################################################################
# The MIT License

# Copyright (c) 2012 ObjectLabs Corporation

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


__author__ = 'abdul'

import string
import types
import sys

from argparse import ArgumentParser
from argparse import ArgumentError
from argparse import HelpFormatter

###############################################################################
# Constants
###############################################################################

OPTIONAL_ARG_TYPE = "optional"
POSITIONAL_ARG_TYPE = "positional"

###############################################################################
# API
###############################################################################
def build_parser(parser_def):
    parser = DargeParser(parser_def)
    setup_parser(parser, parser_def)

    # create subparsers if specified
    children = parser.get_child_definitions()

    if children is not None and len(children) > 0:
        subparsers = parser.add_subparsers()

        for child_def in children:
            childname = child_def["prog"]
            child_parser = subparsers.add_parser(
                childname,
                definition_document=child_def,
                prog = childname,
                parent_dargeparser=parser)
            setup_parser(child_parser, child_def)

    return parser

###############################################################################
def setup_parser(parser, parser_def):
    parser.prog = get_document_property(parser_def, "prog", parser.prog)
    parser.description= get_document_property(parser_def, "description")
    parser.usage = get_document_property(parser_def, "usage")

    #setup args

    arguments = get_document_property(parser_def, "args")

    if arguments is not None and len(arguments) > 0:
        _setup_parser_args(parser, arguments)

    # setup function to call

    func = get_document_property(parser_def, "function")

    if func is not None:
        # check of func is a fully qualified function name and eval it
        if type(func) is types.StringType:
            func = resolve_function(func)

        if callable(func):
            parser.set_defaults(func=func)
        else:
            raise DargeparseException("%s is not callable" % func)

###############################################################################
def _setup_parser_args(parser, arguments):
    for arg_def in arguments:
        argname = get_arg_name(arg_def)
        cmd_arg = get_cmd_arg(arg_def)
        arg_kwargs = make_arg_kwargs(arg_def)
        parser.add_argument(*listify(cmd_arg), **arg_kwargs)


###############################################################################
def make_arg_kwargs(arg_def):
    argname = get_arg_name(arg_def)
    kwargs = {"help": get_document_property(arg_def, "help", "")}

    display_name = get_document_property(arg_def, "displayName")
    if display_name is not None:
        kwargs["metavar"] = display_name

    cmd_arg = get_cmd_arg(arg_def)

    if (cmd_arg is not None and
        argname not in listify(cmd_arg)):
        kwargs["dest"] = argname

    nargs = get_document_property(arg_def, "nargs")
    action = get_document_property(arg_def, "action")

    if nargs is not None:
        if nargs == 0:
            action = "store_true" if action is None else action
        elif nargs > 1:
            kwargs["nargs"] = nargs

    if action is not None:
        kwargs["action"] = action

    default = get_document_property(arg_def, "default")

    kwargs["default"] = default

    return kwargs


###############################################################################
########################                   ####################################
########################     Classes       ####################################
########################                   ####################################
###############################################################################

class DargeHelpFormatter(HelpFormatter):

    ###########################################################################
    def add_usage(self, usage, actions, groups, prefix=None):
        HelpFormatter.add_usage(self, usage, actions, groups, prefix="Usage: ")


###############################################################################
class DargeParser(ArgumentParser):
    ###########################################################################
    # Constructor
    ###########################################################################
    def __init__(self,
                 definition_document=None,
                 prog=None,
                 usage=None,
                 description=None,
                 epilog=None,
                 version=None,
                 parents=[],
                 formatter_class=DargeHelpFormatter,
                 prefix_chars='-',
                 fromfile_prefix_chars=None,
                 argument_default=None,
                 conflict_handler='error',
                 add_help=True,
                 parent_dargeparser=None):
        ArgumentParser.__init__(
            self,
            prog=prog,
            usage=usage,
            description=description,
            epilog=epilog,
            version=version,
            parents=parents,
            formatter_class=formatter_class,
            prefix_chars=prefix_chars,
            fromfile_prefix_chars=fromfile_prefix_chars,
            argument_default=argument_default,
            conflict_handler=conflict_handler,
            add_help=add_help)

        if definition_document is None:
            raise Exception("definition_document cannot be None")
        self.__definition_document__ = definition_document
        self.parent_dargeparser = parent_dargeparser
        self.current_parsing_child = None

    ###########################################################################
    def _check_value(self, action, command_name):
        # converted value must be one of the choices (if specified)
        if action.choices is not None and command_name not in action.choices:

            raise ArgumentError(action, "Unknown command: '%s'\n"
                                        "Enter '%s --help' for a list"
                                        " of commands." %
                                        (command_name, self.prog))

    ###########################################################################
    def print_usage(self, file=None):
        print self.get_usage()

    ###########################################################################
    def print_help(self, file=None):
        print self.get_usage() + '\n'
        print self.description + '\n'
        print self.get_positionals_help()
        print self.get_options_help()
        print self._make_epilog()

    ###########################################################################
    def parse_args(self, raw_args=None, namespace=None):
        args, argv = self.parse_known_args(raw_args, namespace)
        if argv:
            argv_str = ' '.join(argv)
            full_prog = self.get_errored_parser().get_full_prog()
            details_msg = "see '%s --help' for detailed options" % full_prog
            msg =  ("unrecognized arguments: %s" % argv_str +
                    "\n" + self.get_errored_parser().get_usage() +
                    "\n" + details_msg)

            self.error(msg)

        # add additional information
        args.raw_args = raw_args
        def is_arg_specified(arg_name):
            return arg_name in raw_args

        args.is_arg_specified = is_arg_specified

        return args

    ###########################################################################
    def parse_known_args(self, args=None, namespace=None):
        if self.parent_dargeparser is not None:
            self.parent_dargeparser.current_parsing_child = self
        return ArgumentParser.parse_known_args(self,args,namespace)

    ###########################################################################
    def error(self, message):
        if message == "too few arguments":
            self.print_help()
            self.exit(2)

        self.exit(2, message)

    ###########################################################################
    def get_usage(self):
        return self.usage if self.usage else self._make_usage()

    ###########################################################################
    def get_full_prog(self):
        if self.parent_dargeparser is not None:
            return "%s %s" % (self.parent_dargeparser.prog , self.prog)
        else:
            return self.prog

    ###########################################################################
    def _make_usage(self):
        optionals = "[<options>] " if self.has_optional_args() else ""
        positionals = " ".join(self.get_positional_arg_display_names())

        return "Usage: %s %s%s" % (self.prog,
                                    optionals,
                                    positionals)

    ###########################################################################
    def _make_epilog(self):
        return "%s" % self._make_children_epilog()

    ###########################################################################
    def _make_children_epilog(self):
        if not self.has_child_definitions():
            return ""
        ## inlined function
        def _make_child_epilog(child_def):
            child_prog = child_def["prog"]

            return "%s - %s" % (string.ljust(child_prog, 25),
                                child_def['shortDescription'])

        epilog = "Commands:"
        for child_group in self._get_child_groups():
            group_children = self.get_child_definitions_by_group(
                child_group['name'])

            # filter out hidden children
            group_children = filter(lambda child:
                                           not is_hidden_definition(child),
                                    group_children)
            command_list = map(_make_child_epilog ,group_children)

            command_list_string = "\n    ".join(command_list)

            group_display = ""
            if child_group['display']:
                group_display = "%s:" % child_group['display']

            epilog += "\n  %s\n    %s\n" % (group_display, command_list_string)

        epilog_suffix = "See '%s <command> --help' for more help on" \
                        " a specific command." % (self.prog)

        epilog += "\n%s\n" % epilog_suffix
        return epilog

    ###########################################################################
    def get_positionals_help(self):

        # if this is the root parser then positionals help == children help
        # which is done in _make_children_epilog
        if self.parent_dargeparser is None:
            return ""

        formatter = self._get_formatter()
        positional_actions = self._get_positional_actions()
        if positional_actions:
            formatter._indent()
            for action in positional_actions:
                formatter.add_argument(action)

            return "Arguments:\n%s" % formatter.format_help()
        else:
            return ""

    ###########################################################################
    def get_options_help(self):
        formatter = self._get_formatter()
        optional_actions = self._get_optional_actions()
        if optional_actions:
            formatter._indent()
            for action in optional_actions:
                formatter.add_argument(action)

            return "Options:\n%s" % formatter.format_help()
        else:
            return ""

    ###########################################################################
    def _get_child_groups(self):
        child_groups = get_document_property(self.__definition_document__,
                                              "child_groups")
        if child_groups is None or len(child_groups) < 1:
            child_groups = [DEFAULT_CHILD_GROUP]

        return child_groups

    ###########################################################################
    def get_child_definitions_by_group(self, group_name):
        if group_name == DEFAULT_CHILD_GROUP['name']:
            return self.get_child_definitions()
        else:
            return filter(
                lambda child:
                get_document_property(child, "group")  == group_name,
                self.get_child_definitions())

    ###########################################################################
    def get_child_definitions(self):
        return get_document_property(
            self.__definition_document__,
            "children",
            [])

    ###########################################################################
    def has_child_definitions(self):
        children = self.get_child_definitions()
        return children is not None and len(children) > 0

    ###########################################################################
    def get_arg_definitions(self):
        return get_document_property(
            self.__definition_document__,
            "args",
            [])

    ###########################################################################
    def get_optional_args(self):
        return filter(
            lambda arg_def: get_arg_type(arg_def) == OPTIONAL_ARG_TYPE,
                                   self.get_arg_definitions())

    ###########################################################################
    def has_optional_args(self):
        return len(self.get_optional_args()) > 0

    ###########################################################################
    def get_positional_args(self):
        return filter(
            lambda arg_def: get_arg_type(arg_def) == POSITIONAL_ARG_TYPE,
            self.get_arg_definitions())

    ###########################################################################
    def get_positional_arg_names(self):
        return map(
            lambda arg_def: get_arg_name(arg_def), self.get_positional_args())

    ###########################################################################
    def get_positional_arg_display_names(self):
        return map(
            lambda arg_def: get_arg_display_name(arg_def),
            self.get_positional_args())
    ###########################################################################
    def get_parent_dargeparser(self):
        return self.parent_dargeparser

    ###########################################################################
    def get_errored_parser(self):
        if self.current_parsing_child:
            return self.current_parsing_child
        else:
            return self

    ###########################################################################
DEFAULT_CHILD_GROUP = {
    "name" :"allCommands",
    "display": ""
}

###############################################################################
def is_hidden_definition(definition):
    return "hidden" in definition and definition["hidden"]

###############################################################################
#  Arg Definition Functions
###############################################################################
def is_optional_arg(arg_def):
    return get_arg_type(arg_def) == OPTIONAL_ARG_TYPE

###############################################################################
def get_arg_name(arg_def):
    return get_document_property(arg_def, "name")

###############################################################################
def get_arg_type(arg_def):
    return get_document_property(arg_def, "type")

###############################################################################
def get_cmd_arg(arg_def):
    cmd_arg = get_document_property(arg_def, "cmd_arg")
    if cmd_arg is None:
        cmd_arg = get_arg_name(arg_def)

    return cmd_arg

###############################################################################
def get_arg_display_name(arg_def):
    return get_document_property(arg_def, "displayName", get_arg_name(arg_def))

###############################################################################
# Dargeparse Exception class
###############################################################################
class DargeparseException(Exception):
    def __init__(self, message,cause=None):
        self.message  = message
        self.cause = cause

    def __str__(self):
        return self.message

###############################################################################
# Objects Utility Functions
###############################################################################
def listify(object):
    if isinstance(object, list):
        return object

    return [object]

###############################################################################
def get_document_property(document, name, default=None):
    if document.has_key(name):
        return document[name]
    else:
        return default

###############################################################################
def resolve_function(full_func_name):
    names = full_func_name.split(".")
    module_name = names[0]
    module_obj = sys.modules[module_name]
    result = module_obj
    for name in names[1:]:
        result = getattr(result, name)

    return result