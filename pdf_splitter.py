from PyPDF3 import PdfFileReader, PdfFileWriter
import os
from typing import Generator, Callable

PROMPT_STR = '> '

class OutputFile:
    def __init__(self, path: str, name: str, page_interval: tuple[int, int]):
        self.name = name
        self.page_interval = page_interval
        self.current_page = page_interval[0]
        self.stream = open(os.path.join(path, name), 'wb')

    def pages(self) -> Generator[int, None, None]:
        """
        Generator that yields page numbers from start to end of the interval.
        """
        while self.current_page <= self.page_interval[1]:
            yield self.current_page
            self.current_page += 1

    def __str__(self):
        return f'{self.name} ({self.page_interval[0]}-{self.page_interval[1]})'
    
    def __del__(self):
        self.stream.close()

def intro() -> str:
    """
    Prints the intro message and prompts the user for a path to the directory containing the PDF files they want to split.
    If the user presses enter, the current directory is used.
    
    Returns:
        str: The path to the directory containing the PDF files
    """
    print('PDF File Splitter')
    print('Enter the path to the directory containing the PDF files you want to split,\nor press enter to use the current directory.')
    path = input(PROMPT_STR)
    if path == '':
        path = '.'
    return path

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

def get_int(prompt: str, error_msg: str, min: int, max: int) -> int:
    """
    Prompts the user for an integer input within a specified range.
    """
    done = False
    while not done:
        try:
            x = int(input(prompt))
            if min <= x <= max:
                done = True
            else:
                print(error_msg)
        except ValueError:
            print('Please enter a number.')

    return x

def get_file_name(prompt: str, error_msg: str, allow_hidden: bool = False) -> str:
    """
    Prompts the user for a file name and validates it.
    
    Args:
        prompt (str): The prompt to display to the user.
        error_msg (str): The error message to display if validation fails.
        allow_hidden (bool): Allow Linux hidden files (name starting with '.'). Defaults to False.
        
    Returns:
        str: A valid file name.
    """
    # Windows and Unix forbidden characters
    forbidden_chars = '<>:"/\\|?*'
    
    done = False
    while not done:
        name = input(prompt).strip()
        
        # Check for empty file names
        if not name:
            print("File name cannot be empty.")

        # Check for forbidden characters in file name   
        elif any(char in forbidden_chars for char in name):
            print(f"File name cannot contain any of these characters: {forbidden_chars}")
            
        # Check for hidden files
        elif not allow_hidden and name.startswith('.'):
            print("File name cannot start with a dot.")
        
        # Check for long file names
        elif len(name) > 255:
            print("File name is too long. Maximum length is 255 characters.")
            
        # Check if name only contains spaces or dots
        elif not any(c.isalnum() for c in name):
            print("File name must contain at least one letter or number.")

        # Validation OK
        else:
            done = True
            
        return name

def select_file(files: list[str]) -> str:
    """
    Prompts the user to select a file from the list of PDF files.
    Returns:
        str: The name of the selected PDF file
    """
    print('\nSelect a file to split:')
    for i, file in enumerate(files):
        print(f'{i + 1}. {file}')
    
    selection = get_int(PROMPT_STR, 'Please enter a number between 1 and ' + str(len(files)), 1, len(files))

    return files[selection - 1]

def get_output_files(path: str, page_count: int) -> list[OutputFile]:
    """
    Returns a list of OutputFile objects for the selected PDF file, according to the user's input.
    """
    targets = []
    print('\nHow many output files do you want to create?')
    target_count = get_int(PROMPT_STR, 'Please enter a number between 1 and 100', 1, 100)

    for i in range(target_count):
        print('--------------------------------')
        print(f'Output file {i + 1}:')
        name = get_file_name(f'{PROMPT_STR}File name: ', 'Invalid file name')
        start = get_int(f'{PROMPT_STR}First page: ', 'Invalid page number', 1, page_count)
        end = get_int(f'{PROMPT_STR}Last page: ', 'Invalid page number', start, page_count)
        targets.append(OutputFile(path, f'{name}.pdf', (start, end)))

    return targets

def generate_output_files(reader: PdfFileReader, output_files: list[OutputFile], generated_callback: Callable[[OutputFile], None]) -> None:
    """
    Generates output files from the input file.
    """
    for output in output_files:
        writer = PdfFileWriter()

        # Add pages to the writer.
        for page_number in output.pages():
            writer.addPage(reader.getPage(page_number - 1))

        # Write the output file.
        writer.write(output.stream)

        # Call the callback function.
        generated_callback(output)

def main() -> None:
    # Get path from user
    path = intro()
    
    # Get list of PDF files in the directory.
    files = list_pdf_files(path)
    
    # Check if the directory exists.
    if files is None:
        print(f"Directory '{path}' does not exist.")
        return
    
    # If there are no PDF files in the directory, exit.
    if len(files) == 0:
        print('No PDF files found in the directory.')
        return
    
    # Select a file from the list. It will be used as the input file.
    selected_file = select_file(files)

    # Open the input file.
    try:
        input = open(os.path.join(path, selected_file), 'rb')
    except FileNotFoundError:
        print(f'File not found: {selected_file}')
        return
    except IOError:
        print(f'Error reading file: {selected_file}')
        return

    reader = PdfFileReader(input)
    page_count = reader.getNumPages()
    print(f'Selected file: {selected_file} ({page_count} pages)')

    # Get the output files from the user.
    output_files = get_output_files(path, page_count)

    # Generate the output files.
    print('\nGenerating output files...')
    try:
        generate_output_files(reader, output_files, lambda file: print(f'Generated: {file}'))
    except FileNotFoundError:
        print(f'File not found: {selected_file}')
    except IOError:
        print(f'Error reading file: {selected_file}')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')

    # Close the input file and exit.
    input.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Exiting...')
