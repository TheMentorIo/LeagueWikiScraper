"""
Utility functions for League of Legends Wiki Scraper
"""
import hashlib
import os
from typing import Union

import champion_scraper


class Utils:
    """Utility class with helper functions"""
    
    @staticmethod
    def sanitize(text: str) -> str:
        """
        Sanitize text for use as filename
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text safe for filenames
        """
        return text.replace(" ", "_").replace("/", "-").replace('"', "").replace("'", "").strip()
    
    @staticmethod
    def compute_hash(data: Union[bytes, str]) -> str:
        """
        Compute SHA256 hash of data
        
        Args:
            data: Data to hash (bytes or string)
            
        Returns:
            Hexadecimal hash string
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def compute_file_hash(file_path: str) -> str:
        """
        Compute SHA256 hash of a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Hexadecimal hash string
        """
        with open(file_path, 'rb') as f:
            return Utils.compute_hash(f.read())
    
    @staticmethod
    def ensure_directory(path: str) -> None:
        """
        Ensure a directory exists, create if it doesn't
        
        Args:
            path: Directory path to ensure
        """
        os.makedirs(path, exist_ok=True)
    
    @staticmethod
    def get_file_extension(url: str, default: str = ".png") -> str:
        """
        Extract file extension from URL
        
        Args:
            url: URL to extract extension from
            default: Default extension if none found
            
        Returns:
            File extension with dot
        """
        ext = os.path.splitext(url)[1]
        return ext if ext else default 
