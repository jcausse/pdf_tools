from typing import Generator

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
