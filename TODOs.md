Temos no momento 3 arquivos de exemplo:
- /home/marco/workspace/projects/rand_engine/rand_engine/examples/advanced_rand_specs.py
- /home/marco/workspace/projects/rand_engine/rand_engine/examples/spark_examples.py
- /home/marco/workspace/projects/rand_engine/rand_engine/examples/spark_rand_specs.py


Gostaria de renomear /home/marco/workspace/projects/rand_engine/rand_engine/examples/spark_rand_specs.py para /home/marco/workspace/projects/rand_engine/rand_engine/examples/common_rand_specs.py

Nesse arquivo renomeado para /home/marco/workspace/projects/rand_engine/rand_engine/examples/common_rand_specs.py temos exemplos de especificações randômicas comuns que podem ser usadas com o DataGenerator e o SparkGenerator.

Em /home/marco/workspace/projects/rand_engine/rand_engine/examples/spark_examples.py Temos somente exemplos de uso do SparkGenerator.

Gostaria de manter somente /home/marco/workspace/projects/rand_engine/rand_engine/examples/common_rand_specs.py e apagar o arquivo /home/marco/workspace/projects/rand_engine/rand_engine/examples/spark_rand_specs.py. Faça as alterações necessárias no pacote e em imports para testes conforme necessário. Ao final teremos somente 2 arquivos de exemplo:

- /home/marco/workspace/projects/rand_engine/rand_engine/examples/advanced_rand_specs.py
- /home/marco/workspace/projects/rand_engine/rand_engine/examples/common_rand_specs.py