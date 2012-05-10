__author__ = 'abdul'


import dargparse
import datetime
import unittest

from dargparse import dargparse
from datetime import datetime
from unittest import  TestCase
###############################################################################
# Constants
###############################################################################
HELLO_PARSER ={
    "prog": "hello-dargparse",
    "description" : "This is hello world dargparse example",
    "args": [
            {
            "name": "yourName",
            "type" : "positional",
            "help": "Your name",
            "metavar" : "<YOUR NAME>",
            "nargs": 1
        },
            {
            "name": "printDate",
            "type" : "optional",
            "help": "print the current date",
            "cmd_arg": [
                "-d",
                "--printDate"
            ],
            "nargs": 0,
            "action": "store_true",
            "default": False
        }

    ]


}


helloDargParser = None
###############################################################################
# SimpleDargparseTest class
###############################################################################
class SimpleDargparseTest(unittest.TestCase):

    ###########################################################################
    def setUp(self):
        global helloDargParser
        helloDargParser = dargparse.build_parser(HELLO_PARSER)
    ###########################################################################
    def tearDown(self):
        pass
    ###########################################################################
    def test_simple(self):
    # parse the command line
        args = ["--printDate" , "Abdulito"]
        global helloDargParser
        parsed_options = helloDargParser.parse_args(args)
        now = datetime.now()
        if parsed_options.printDate:
            print "Hello %s! the time now is %s" % (parsed_options.yourName,now)
        else:
            print "Hello %s!" % (parsed_options.yourName)