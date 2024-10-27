

class DistinctUtils:

  @classmethod
  def handle_distincts_lvl_1(self, distinct_prop, precision):
    return [ key for key, value in distinct_prop.items() for i in range(value * precision )]

  @classmethod
  def handle_distincts_lvl_2(self, distincts, sep=";"):
    data_flatted = [f"{j}{sep}{i}" for j in distincts for i in distincts[j]]
    return data_flatted

  @classmethod
  def handle_distincts_lvl_3(self, distincts, sep=";"):
    parm_paired_distincts = {k: list(map(lambda x: f"{x[0]}@!{x[1]}", v)) for k, v in distincts.items()}
    data_flatted = self.handle_distincts_lvl_2(parm_paired_distincts, sep)
    result = []
    for i in data_flatted:
      value, size = i.split("@!")
      result.extend([value for _ in range(int(size))])
    return result
  