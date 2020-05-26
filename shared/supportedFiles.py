from enum import Enum, unique

@unique
class SupportedFiles(Enum):
    """ formatos de ficheros soportados """
    EXCEL= 10
    CSV = 20