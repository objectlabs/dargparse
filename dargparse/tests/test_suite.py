import unittest

from simple_dargparse_test import SimpleDargparseTest
###############################################################################
all_suites = [
    unittest.TestLoader().loadTestsFromTestCase(SimpleDargparseTest)
]
###############################################################################
# booty
###############################################################################
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(all_suites))


