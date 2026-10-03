import os
from typing import List
import uuid
from rand_engine.file_handlers.file_handler import FileHandler
from rand_engine.file_handlers.writer import FileWriter


class FileBatchWriter(FileWriter):


  def __init__(self, microbatch_def):
    super().__init__(microbatch_def)
  

  def __handle_filenames(self, path: str, size: int, ext) -> List[str]:
    return [f"{path}/part_{str(uuid.uuid4())[:18]}.{ext}" for _ in range(size)]


  def __generate_file(self, path, dataframe, write_options):
    self.writer_method[self.write_format](dataframe, path, write_options)()

  def save(self, path: str) -> None:

    write_options = dict(self.write_options)
    num_files = write_options.pop("numFiles", 1)

    base_path, file_name, ext = FileHandler.handle_path(path, self.write_format, write_options)
    if num_files > 1:
      path = f"{base_path}/{file_name}"
      files = self.__handle_filenames(path, num_files, ext)
    else: files = [f"{base_path}/{file_name}.{ext}"]
    dataframes = [self.microbatch_def() for _ in files]
    os.makedirs(os.path.dirname(files[0]), exist_ok=True)
    if num_files > 1 and self.write_mode == "overwrite":
      if os.path.exists(path):
        for f in os.listdir(path):
          os.remove(os.path.join(path, f))
      
    for file, dataframe in zip(files, dataframes):
      self.__generate_file(file, dataframe, write_options)

