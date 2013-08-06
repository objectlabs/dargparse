#### Overview
Declarative command-line argument parser for python


#### A simple example



```
/home/abdul/objectlabs/dargparse/hello-dargparse

#!/usr/bin/env python


import dargparse
import sys
import traceback
import datetime

from dargparse import dargparse
from datetime import  datetime

# Define your parse dictionary

HELLO_PARSER ={
    "prog": "hello-dargparse",
    "description" : "This is hello world dargparse example",
    "args": [
        {
            "name": "yourName",
            "type" : "positional",
            "help": "Your name",
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
        },
        {
            "name": "repeat",
            "type" : "optional",
            "help": "repeat for N times",
            "cmd_arg": [
                "-r",
                "--repeat"
            ],
            "nargs": 1,
            "default": 1,
            "valueType": int,
        }

    ]


}



###############################################################################
# MAIN
###############################################################################
def main(args):
    # build the parse object
    helloDargParser = dargparse.build_parser(HELLO_PARSER)

    # parse the command line

    parsed_options = helloDargParser.parse_args(args)
    now = datetime.now()
    if parsed_options.printDate:
        msg = "Hello %s! the time now is %s" % (parsed_options.yourName,now)
    else:
        msg = "Hello %s!" % (parsed_options.yourName)
    print '\n'.join([msg] * parsed_options.repeat)


###############################################################################
########################                   ####################################
########################     BOOTSTRAP     ####################################
########################                   ####################################
###############################################################################

if __name__ == '__main__':
    try:
        # call main with a sub-list starting skipping the
        # "hello-dargparse" command itself (which is the first arg)
        main(sys.argv[1:])
    except (SystemExit, KeyboardInterrupt) , e:
        if e.code == 0:
            pass
        else:
            raise
    except:
        traceback.print_exc()


```

Execute your example

```
[abdul:~/objectlabs/dargparse] ./hello-dargeparse
Usage: hello-dargparse [<options>] yourName

This is hello world dargparse example

Options:
  -h, --help       show this help message and exit
  -d, --printDate  print the current date


[abdul:~/objectlabs/dargparse] ./hello-dargeparse abdul
Hello abdul!


[abdul:~/objectlabs/dargparse] ./hello-dargeparse -d abdul
Hello abdul! the time now is 2012-03-20 00:32:04.129220


[abdul:~/objectlabs/dargparse] ./hello-dargeparse -d -r 3 abdul
Hello abdul! the time now is 2012-03-20 00:32:05.496178
Hello abdul! the time now is 2012-03-20 00:32:05.496178
Hello abdul! the time now is 2012-03-20 00:32:05.496178

with "required" set on date flag:
[abdul:~/objectlabs/dargparse] ./hello-dargeparse abdul
argument -d/--printDate is required

[abdul:~/objectlabs/dargparse] ./hello-dargeparse -printDate abdul
unrecognized arguments: -printDate
Usage: hello-dargparse [<options>] yourName
see 'hello-dargparse --help' for detailed options

[abdul:~/objectlabs/dargparse] ./hello-dargeparse -blah bloh
unrecognized arguments: -blah
Usage: hello-dargparse [<options>] yourName
see 'hello-dargparse --help' for detailed options%

```

Requirements
--------------------

* Python >= 2.7
* pip >= 1.0.2
   + Download: http://pypi.python.org/pypi/pip#downloads
   + Operating instructions: http://www.pip-installer.org/en/latest/index.html
   + Installation instructions: http://www.pip-installer.org/en/latest/index.html

Installing pip from git is the easiest:

```
% git clone https://github.com/pypa/pip.git
% cd pip
% python setup.py install # may need to be root or need to use sudo
```

Installing
--------------------

```
 sudo pip install dargparse
```
