from enum import Enum


    
class LogLevel(Enum):
    error = 1
    critical = 2
    warning = 3
    info = 4

def log(logLevel, data):
    print(data)
