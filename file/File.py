"""
File system data structures and classes
- Block: Physical disk block
- FAT: File Allocation Table
- FCB: File Control Block
- CatalogNode: Directory structure node
"""
from typing import List, Optional, Union
import time

# Constants
BLOCK_SIZE = 512
BLOCK_NUM = 512

class Block:
    """
    A physical block in the disk storage
    """
    def __init__(self, block_index: int, data: str = ""):
        self.block_index = block_index
        self.data = data
    
    def write(self, new_data: str) -> str:
        """
        Write data to block and return remaining data that couldn't fit
        """
        self.data = new_data[:BLOCK_SIZE]
        return new_data[BLOCK_SIZE:]
    
    def read(self) -> str:
        """
        Read data from block
        """
        return self.data

    def is_full(self) -> bool:
        """
        Check if block is full
        """
        return len(self.data) == BLOCK_SIZE

    def append(self, new_data: str) -> str:
        """
        Append new data to block and return data that couldn't fit
        """
        remain_space = BLOCK_SIZE - len(self.data)
        if remain_space >= len(new_data):
            self.data += new_data
            return ""
        else:
            self.data += new_data[:remain_space]
            return new_data[remain_space:]
    
    def clear(self) -> None:
        """
        Clear block data
        """
        self.data = ""


class FAT:
    """
    File Allocation Table implementation
    """
    def __init__(self):
        self.fat: List[int] = [-2] * BLOCK_NUM

    def find_blank(self) -> int:
        """
        Find first available block
        """
        for i in range(BLOCK_NUM):
            if self.fat[i] == -2:
                return i
        return -1
    
    def write(self, data: str, disk: List[Block]) -> int:
        """
        Write data to disk, allocating blocks as needed
        Returns the starting block index
        """
        start = -1
        cur = -1

        while data:
            new_loc = self.find_blank()
            if new_loc == -1:
                raise Exception("Disk space insufficient!")
            
            if cur != -1:
                self.fat[cur] = new_loc
            else:
                start = new_loc
                
            cur = new_loc
            data = disk[cur].write(data)
            self.fat[cur] = -1

        return start
    
    def delete(self, start: int, disk: List[Block]) -> None:
        """
        Delete file chain starting at given block
        """
        if start == -1:
            return

        while self.fat[start] != -1:
            disk[start].clear()
            next_block = self.fat[start]
            self.fat[start] = -2
            start = next_block

        self.fat[start] = -2
        disk[start].clear()
    
    def update(self, start: int, data: str, disk: List[Block]) -> int:
        """
        Update file data by deleting old chain and writing new data
        """
        self.delete(start, disk)
        return self.write(data, disk)

    def read(self, start: int, disk: List[Block]) -> str:
        """
        Read file data from block chain
        """
        if start == -1:
            return ""
            
        data = ""
        current = start
        
        while True:
            data += disk[current].read()
            if self.fat[current] == -1:
                break
            current = self.fat[current]
            
        return data


class FCB:
    """
    File Control Block for managing file metadata
    """
    def __init__(self, name: str, create_time: time.struct_time, data: str, fat: FAT, disk: List[Block]):
        self.name = name
        self.create_time = create_time
        self.update_time = self.create_time
        self.start = fat.write(data, disk) if data else -1
    
    def update(self, new_data: str, fat: FAT, disk: List[Block]) -> None:
        """
        Update file content
        """
        self.start = fat.update(self.start, new_data, disk)
        self.update_time = time.localtime()
    
    def delete(self, fat: FAT, disk: List[Block]) -> None:
        """
        Delete file from disk
        """
        fat.delete(self.start, disk)
    
    def read(self, fat: FAT, disk: List[Block]) -> str:
        """
        Read file content
        """
        if self.start == -1:
            return ""
        return fat.read(self.start, disk)


class CatalogNode:
    """
    Directory tree node for multi-level directory structure
    """
    def __init__(self, name: str, is_file: bool, fat: FAT, disk: List[Block], 
                 create_time: time.struct_time, parent: Optional['CatalogNode'] = None, 
                 data: str = ""):
        self.name = name
        self.is_file = is_file
        self.parent = parent
        self.create_time = create_time
        self.update_time = self.create_time
        
        if not self.is_file:
            self.children: List['CatalogNode'] = []
        else:
            self.data = FCB(name, create_time, data, fat, disk)
        