from fastapi import UploadFile
from typing import List, AnyStr

class FileValidator:

    audio_extensions: List[AnyStr] = [".ogg", ".mp3", ".wav"]
    image_extensions: List[AnyStr] = [".jpg", ".png", ".gif", ".svg"]
    video_extensions: List[AnyStr] = [".mp4", ".avi", ".mov", ".flv"]
    document_extensions: List[AnyStr] = [".pdf", ".docx", ".doc", ".txt", ".xls", ".rtf"]
    default_size_mb = 10

    def __init__(self, file: UploadFile, max_size_mb: int = default_size_mb) -> bool:
        self.file = file
        self.max_size_mb = max_size_mb

    def validate(self) -> bool:
        return self.vaildate_type() and self.validate_size()

    def vaildate_type(self, extensions: List[AnyStr] = audio_extensions) -> bool:
        return self.file.filename.endswith(tuple(extensions))
    
    def validate_size(self, size: int = None) -> bool:
        bytes_in_kilobyte = 1024
        bytes_in_megabyte = bytes_in_kilobyte * 1024
        valid_size = size if size else self.max_size_mb
        return self.file.size <= valid_size * bytes_in_megabyte