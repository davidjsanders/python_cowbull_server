import unittest
from TestGameController import TestGameController
from TestV1Routes import TestV1Routes
from TestGameMode import TestGameMode
from TestErrorHandler import TestErrorHandler
from TestConfigurator import TestConfigurator

if __name__ == '__main__':
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='systest-reports'))
