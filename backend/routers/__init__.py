from .story import router as story_router
from .history import router as history_router
from .config import router as config_router
from .works import router as works_router

__all__ = ['story_router', 'history_router', 'config_router', 'works_router']
