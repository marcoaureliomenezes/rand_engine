import os
from typing import List
from rand_engine.file_handlers.file_handler import FileHandler
from rand_engine.file_handlers.writer import FileWriter


class FileBatchWriter(FileWriter):


  def __init__(self, microbatch_def):
    super().__init__(microbatch_def)
  

  def __handle_filenames(self, path: str, size: int) -> List[str]:
    return [f"{path}/part_{str(i).zfill(5)}.{self.write_format}" for i in range(size)]


  def __generate_file(self, path):
    dataframe = self.microbatch_def(self._size)
    self.writer_method[self.write_format](dataframe, path, self.write_options)()

  def save(self, path: str) -> None:
    num_files = self.write_options.get("numFiles", 1)
    del self.write_options["numFiles"]

    base_path, file_name, ext = FileHandler.handle_path(path, self.write_format, self.write_options)
    if num_files > 1:
      path = f"{base_path}/{file_name}"
      files = self.__handle_filenames(path, num_files)
    else: files = [f"{base_path}/{file_name}{ext}"]
    os.makedirs(os.path.dirname(files[0]), exist_ok=True)
    for file in files:
      self.__generate_file(file)

