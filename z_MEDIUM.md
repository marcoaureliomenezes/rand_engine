Rand-Engine: Gerando dados para testes

Desde que comecei a estudar tópicos relativos a engenharia de dados um aspecto sempre me intrigou. Depender daquele arquivo CSV como entrada para testar regras simples.
Em termos gerais um job de processamento de dados pode ser encarado como uma rotina que tem por finalidade a partir de uma entrada de dados gerar uma saída. 
É aquele caso genérico onde existe um CSV de n campos, armazenado em um local onde o Job de processamento consegue ler. E então esse CSV é lido, carregado em memória pelo job, transformações são efetuadas e o resultado é gravado. É claro, quando estamos lidando com processamento Batch.