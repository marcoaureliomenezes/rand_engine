Perfeito. Agora quero renomear a classe ExampleSpecs para RandSpecs. Quero que seja uma classe estática, ou seja, que não precise ser instanciada para ser usada. Quero que todos os métodos sejam de classe (classmethod) e que os atributos sejam atributos de classe.


Atualize outros arquivos para que não haja mais referência à classe ExampleSpecs, mas sim à RandSpecs.

Use os ExamplesSpecs do módulo rand_engine.main.examples para atualizar o README.md



Muito bom. Agora que temo o módulo /home/marco/workspace/projects/rand_engine/rand_engine/main/examples.py, acredito que fica muito melhor para os usuários importarem os exemplos somente é necessário importar o rand_engine.main.examples RandSpecs.


Gostaria que melhorasse nosso arquivo README.md. Além de deixar claro como é possível ver esses exemplos, agora é possível reduzir a complexidade do README.md, resumindo-se as inúmeras configurações de random_spec passadas no README.md, o que acredito que pode confundir novos usuários.


Reavalie a lib e atualize o /home/marco/workspace/projects/rand_engine/README.md. Lembre-se que ele deve ser escrito em inglês e deve conter exemplos de uso simples para que engenheiros de dados, QA engineers e outros possam aprender rápido e se apaixonar pela lib.