import os
import time
from typing import Generator
import uuid
from rand_engine.file_handlers.file_handler import FileHandler
from rand_engine.file_handlers.writer import FileWriter


class FileStreamWriter(FileWriter):


  def __init__(self, size_def, microbatch_def):
    super().__init__(size_def, microbatch_def)
    self.freq = 1
  

  def trigger(self, frequency: int):
    self.freq = frequency
    return self


  def __handle_filenames(self, path: str, ext: str) -> Generator:
    while True:
      yield f"{path}/part-{str(uuid.uuid4())}.{ext}"

  def __generate_file(self, path, dataframe, write_options):
    self.writer_method[self.write_format](dataframe, path, write_options)()
    

  def start(self, path):
    base_path, file_name_cleaned, ext = FileHandler.handle_path(path, self.write_format, self.write_options)
    path = f"{base_path}/{file_name_cleaned}"
    size = self.size_def()
    dataframe, offset = self.microbatch_def(size, 0), size
    os.makedirs(path, exist_ok=True)
    if self.write_mode == "overwrite":
      if os.path.exists(path):
        for f in os.listdir(path):
          os.remove(os.path.join(path, f))
    write_options = dict(self.write_options)
    timeout = write_options.pop("timeout", 20)
    start_time = time.time()
    file_gen = self.__handle_filenames(path, ext)
    for file in file_gen:
      self.__generate_file(file, dataframe, write_options)
      time.sleep(self.freq)
      if time.time() - start_time > timeout: break
      size = self.size_def()
      dataframe, offset = self.microbatch_def(size, offset), offset + size
