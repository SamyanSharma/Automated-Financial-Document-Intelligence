"""
Import all models here so that Base.metadata is fully populated wherever
`from database import Base` + `import models` happens (needed for both
`init_db()`'s create_all and for Alembic's autogenerate to see every table).
"""
from models.user import User  # noqa: F401
from models.document import Document, DocumentChunk, DocumentStatus  # noqa: F401

__all__ = ["User", "Document", "DocumentChunk", "DocumentStatus"]
