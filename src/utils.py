import os
import platform
import json

osName = platform.system()

with open(f'./cmd/{ "windows" if osName == "Windows" else "linux" }.json') as f:
    cmd = json.load(f)

def printTree(dirPath, indent=''):
    for item in os.listdir(dirPath):
        itemPath = os.path.join(dirPath, item)
        if os.path.isdir(itemPath):
            print(f'{ indent }+ { item }/')
            printTree(itemPath, indent + ' ')
        else:
            print(f'{ indent }- { item }')

def countChildren(dirPath):
    count = 0
    for item in os.listdir(dirPath):
        itemPath = os.path.join(dirPath, item)
        count += 1
    return count

class Clear:
    def __init__(self, toggle = True) -> None:
        self.toggled = toggle
    
    def toggleClear(self, enable):
        self.disableClear = enable

    def clearScreen(self):
        if self.toggled:
            os.system(cmd['general']['clear'])