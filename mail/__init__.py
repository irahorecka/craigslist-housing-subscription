import os
from ._threading import map_threads
from .send_email import write_email

# Check if environment variables exist for sender email and password
if not os.environ.get("EMAIL_USER") or not os.environ.get("EMAIL_PASS"):
    raise ValueError(
        "No value for 'EMAIL_USER' and/or 'EMAIL_PASS'. Please configure these environment variables."
    )
