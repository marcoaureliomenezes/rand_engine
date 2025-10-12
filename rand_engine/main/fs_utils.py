"""
File System Handler Classes

This module provides different implementations to handle file system operations
both for local Linux filesystem and Databricks File System (DBFS).

Classes:
    FSUtils: Abstract base class defining the interface
    LocalFSUtils: Implementation for local Linux filesystem
    DBFSUtils: Implementation for Databricks File System (DBFS)
"""

import os
import glob
from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass


@dataclass
class FSFileInfo:

    path: str
    name: str
    size: int
    modificationTime: int


class FSUtils(ABC):
    
    @abstractmethod
    def ls(self, base_path: str) -> List[FSFileInfo]:
        pass
    
    @abstractmethod
    def mkdir(self, path: str) -> None:
        pass
    
    @abstractmethod
    def rm(self, path: str) -> None:
        pass


class LocalFSUtils(FSUtils):
    
    def ls(self, path: str) -> List[FSFileInfo]:
        if not os.path.exists(path):
            return []
        
        items = []
        
        # If path is a file, return info about the file itself
        if os.path.isfile(path):
            stat_info = os.stat(path)
            items.append(FSFileInfo(
                path=path,
                name=os.path.basename(path),
                size=stat_info.st_size,
                modificationTime=int(stat_info.st_mtime * 1000)
            ))
        # If path is a directory, list its contents (non-recursive)
        elif os.path.isdir(path):
            for item_name in os.listdir(path):
                item_path = os.path.join(path, item_name)
                stat_info = os.stat(item_path)
                
                # For directories, size is 0; for files, use actual size
                size = stat_info.st_size if os.path.isfile(item_path) else 0
                
                items.append(FSFileInfo(
                    path=item_path,
                    name=item_name,
                    size=size,
                    modificationTime=int(stat_info.st_mtime * 1000)
                ))
        return sorted(items, key=lambda x: x.path)
    

    def mkdir(self, path: str) -> None:
        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            raise Exception(f"Failed to create directory {path}: {str(e)}")


    def rm(self, path: str, recursive: bool = False) -> None:
        try:
            if os.path.isdir(path) and recursive:
                import shutil
                shutil.rmtree(path)
            elif os.path.isfile(path):
                os.remove(path)
            else:
                raise Exception(f"Path {path} does not exist or is not a file.")
        except Exception as e:
            raise Exception(f"Failed to delete file {path}: {str(e)}")



class DBFSUtils(FSUtils):
    
    def __init__(self):
        try:
            from pyspark.dbutils import DBUtils
            from pyspark.sql import SparkSession 
            spark = SparkSession.getActiveSession()
            if spark is None:
                raise Exception("No active Spark session found")        
            self.dbutils = DBUtils(spark)
        except Exception as e:
            raise ImportError(f"DBUtils not available. Are you running in Databricks? Error: {str(e)}")
    
    def ls(self, base_path: str) -> List[FSFileInfo]:
        try: 
            data = self.dbutils.fs.ls(base_path)
            return [FSFileInfo(
                path=item.path.replace("dbfs:", ""),
                name=item.name,
                size=item.size,
                modificationTime=item.modificationTime
            ) for item in data]
        except Exception as e:
            return []
    

    def mkdir(self, path: str) -> None:
        try: self.dbutils.fs.mkdirs(path)
        except Exception as e:
            raise Exception(f"Failed to create directory {path}: {str(e)}")
    

    def rm(self, path: str, recursive: bool = False) -> None:
        try:
            result = self.dbutils.fs.rm(path, recursive)
            if not result:
                raise Exception(f"Failed to delete file {path}")
        except Exception as e:
            raise Exception(f"Failed to delete file {path}: {str(e)}")



    def __get_dir_size(self, folder_path: str) -> int:
        """
        This method calculates the size in bytes of a directory.
        :param folder_path: str: Path of the directory.
        :return: int: Size of the directory in bytes.
        """
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if not os.path.islink(file_path):
                    total_size += os.path.getsize(file_path)
        return total_size
  

# def __handle_fs(self, path, flag=True) -> None:
#   """
#   This method handles the file system operations.
#   :param path: str: Path of the file to be written.
#   """
#   if self.write_mode == "overwrite":
#     try:
#       if os.path.exists(path):
#         for file in os.listdir(path):
#           os.remove(os.path.join(path, file))
#     except Exception as e: pass
#   if flag == True: to_create = os.path.dirname(path)
#   else: to_create = path
#   os.makedirs(to_create, exist_ok=True)
