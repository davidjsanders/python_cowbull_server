import unittest
# Import required tests - Note new package placement.
from tests.TestV1Routes import TestV1Routes
from tests.TestGameController import TestGameController
from tests.TestGameObject import TestGameObject
from tests.TestGameMode import TestGameMode
from tests.TestErrorHandler import TestErrorHandler
from tests.TestConfigurator import TestConfigurator
from tests.TestHelpers import TestHelpers
from tests.TestPersister import TestPersister
from tests.TestPersisterMongo import TestPersisterMongo

if __name__ == '__main__':
    unittest.main()
