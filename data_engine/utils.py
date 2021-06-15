from performance.perform import performance

@performance
def sum(a, b):
    return [a + b]

print(sum(2,3))