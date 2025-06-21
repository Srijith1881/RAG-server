# Utility functions for the PDF service
import uuid

def generate_file_id():
    # Generates a UUID string to be used as a file ID.

    return str(uuid.uuid4())
