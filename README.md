# Pacote Rand-Engine


O pacote **Rand-Engine** consiste de um conjunto de classes, associando funcionalidades dos pacotes `random`, `numpy` e `pandas` para finalidade de estudos e testes. 

## Classes Core

As classes core são do tipo estáticas, ou seja, não é necessário instanciar um objeto para utilizá-las. As classes core são:

- **CoreDistinct**: Classe com métodos para gerar valores aleatórios distintos.
- **CoreNumeric**: Classe com métodos para gerar valores numéricos aleatórios.
- **CoreDatetime**: Classe com métodos para gerar valores de data e hora aleatórios.



## Core Distinct

Na classe CoreDistinct, é possível gerar dados aleatórios distintos, ou seja, sem repetição. 

```python
from rand_engine.bulk.core_distincts import CoreDistincts

CoreDistinct().randint(0, 100, 10)

```

## Release Process

To create a new release, simply create and push a git tag with semantic versioning:

```bash
git tag 0.3.13 && git push origin --tags
```

The GitHub Actions workflow will automatically:
- Build and test the package
- Publish to PyPI
- Create a GitHub Release
- Update the Homebrew formula (if configured)