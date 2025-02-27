class BaseParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
    
    def parse(self):
        """Parse the input file and return the data"""
        raise NotImplementedError("Each parser must implement this method")
    
    def validate(self):
        """Validate the parsed data"""
        raise NotImplementedError("Each parser must implement this method")
