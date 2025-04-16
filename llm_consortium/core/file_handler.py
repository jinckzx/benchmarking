import magic
from pathlib import Path
from typing import Union

class FileHandler:
    def __init__(self, upload_dir="data/raw_files"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.mime = magic.Magic(mime=True)

    def validate_file(self, uploaded_file) -> bool:
        """Validate allowed file types"""
        allowed_types = [
            'application/pdf',
            'text/plain',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/csv'
        ]
        file_type = self.mime.from_buffer(uploaded_file.getbuffer())
        return file_type in allowed_types

    def save_file(self, uploaded_file) -> Path:
        """Save uploaded file with collision handling"""
        save_path = self.upload_dir / uploaded_file.name
        if save_path.exists():
            save_path = self.upload_dir / f"{uuid.uuid4()}_{uploaded_file.name}"
        
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return save_path