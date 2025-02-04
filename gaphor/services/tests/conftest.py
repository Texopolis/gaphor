import pytest

from gaphor.diagram.tests.fixtures import (
    diagram,
    element_factory,
    event_manager,
    modeling_language,
)
from gaphor.services.undomanager import UndoManager


@pytest.fixture
def undo_manager(event_manager, element_factory):
    undo_manager = UndoManager(event_manager, element_factory)
    yield undo_manager
    undo_manager.shutdown()
