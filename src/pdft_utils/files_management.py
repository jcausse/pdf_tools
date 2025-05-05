import os

def list_pdf_files(directory_path: str) -> (list[str] | None):
    """
    Lists all PDF files in the specified directory.
    
    Args:
        directory_path (str): Path to the directory to search for PDFs
        
    Returns:
        list[str] | None: A list of PDF filenames found in the directory, or None if the directory does not exist
    """
    # Check if the directory exists
    if not os.path.exists(directory_path):
        return None
    
    pdf_files = []
    
    # List all files and filter for .pdf extension
    for file in os.listdir(directory_path):
        if file.lower().endswith('.pdf'):
            pdf_files.append(file)
    
    return pdf_files
