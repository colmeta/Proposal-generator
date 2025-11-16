"""Services package"""
# Import background processor (Agent 2)
from services.background_processor import BackgroundProcessor, background_processor

# Import storage service (Agent 1) - optional if not created yet
try:
    from services.storage import StorageService, storage_service
    __all__ = [
        "StorageService",
        "storage_service",
        "BackgroundProcessor",
        "background_processor",
    ]
except ImportError:
    __all__ = [
        "BackgroundProcessor",
        "background_processor",
    ]

# Import knowledge base (Agent 4) - optional if not created yet
try:
    from services.knowledge_base import KnowledgeBase
    __all__.append("KnowledgeBase")
except ImportError:
    pass
