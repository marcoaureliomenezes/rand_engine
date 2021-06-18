import random, unittest

# Remove all duplicated items, but the replacement is not in the same position.
# it's perfect to random data.
def replace_duplicate(lista, replace):
    result = list(set(lista))
    result.extend([replace for i in range(len(lista)-len(result))])
    random.shuffle(result)
    return result

if __name__ == '__main__':
    unittest.main()