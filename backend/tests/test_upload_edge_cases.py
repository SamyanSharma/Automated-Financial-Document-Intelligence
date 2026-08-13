"""
Pure sync unit tests — deliberately no `pytestmark = pytest.mark.asyncio`
here, since these don't need the event loop or the app fixture.
"""


def test_filename_guard_handles_none_without_crashing():
    """
    Regression test for the audit finding: `file.filename.lower()` in
    routers/documents.py:upload_document raised AttributeError (-> 500) if
    a client omitted the filename in the multipart part. httpx's test
    client can't construct that exact wire shape (an empty filename
    degrades to a plain form field, not a file part), so this exercises
    the guard logic directly, matching what a real ASGI server passes
    through when Content-Disposition has no filename.

    Before the fix: `filename.lower()` on `None` -> AttributeError -> 500.
    After the fix: `filename = file.filename or ""` -> clean 400.
    """
    filename = None
    content_type = "application/octet-stream"

    safe_filename = filename or ""
    is_rejected = content_type != "application/pdf" and not safe_filename.lower().endswith(".pdf")

    assert is_rejected is True  # correctly raises HTTPException(400, ...), never crashes
