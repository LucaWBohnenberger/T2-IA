import random
import copy

matriz_escola_a = [
    [1, 2, 4, 3],  # Preferências do aluno A1
    [2, 3, 1, 4],  # Preferências do aluno A2
    [4, 1, 3, 2],  # Preferências do aluno A3
    [3, 1, 2, 4],  # Preferências do aluno A4
]

matriz_escola_b = [
    [3, 2, 4, 1],  # Preferências do aluno B1
    [3, 2, 4, 1],  # Preferências do aluno B2
    [2, 4, 3, 1],  # Preferências do aluno B3
    [1, 3, 4, 2],  # Preferências do aluno B4
]

n = 4
lista = [i for i in range(1, n + 1)]
lista2 = [i for i in range(1, n + 1)]


def funcao_heuristica(matriz_alocacao, matriz_escola_a, matriz_escola_b):
    losses = []
    for alocacao in matriz_alocacao:
        loss = 0
        for aluno_a, aluno_b in alocacao:
            loss += matriz_escola_a[aluno_a - 1].index(aluno_b)
            loss += matriz_escola_b[aluno_b - 1].index(aluno_a)
        losses.append(loss)
    return losses


matriz_alocacao = []
for _ in range(10):
    lista = [i for i in range(1, n + 1)]
    lista2 = [i for i in range(1, n + 1)]
    alocacao = []
    for i in range(n):
        val1 = random.choice(lista)
        lista.remove(val1)
        val2 = random.choice(lista2)
        lista2.remove(val2)
        alocacao.append((val1, val2))
    matriz_alocacao.append(alocacao)


def mostrar(matriz_alocacao, losses):
    print()
    new = copy.deepcopy(matriz_alocacao)
    for i in range(len(losses)):
        new[i].append(losses[i])
        print(new[i])


def elitismo(matriz_alocacao, losses):
    index = losses.index(min(losses))

    return copy.deepcopy(matriz_alocacao[index])


def torneio(matriz_alocacao, losses):
    lista = [i for i in range(1, 10)]
    index1, index2 = random.sample(lista, 2)
    if losses[index1] < losses[index2]:
        return copy.deepcopy(matriz_alocacao[index1])
    else:
        return copy.deepcopy(matriz_alocacao[index2])


# Pensar com mais calma em como fazer o crossover
# Crossover baseado no pmx
def crossover(pai, mae):
    x_pai = [i[0] for i in pai]
    y_pai = [i[1] for i in pai]
    x_mae = [i[0] for i in mae]
    y_mae = [i[1] for i in mae]
    val1, val2 = sorted(random.sample(range(0, n), 2))

    for i in range(val1, val2 + 1):
        index_pai = x_pai.index(x_mae[i])
        index_mae = x_mae.index(x_pai[i])
        x_pai[i], x_pai[index_pai] = x_pai[index_pai], x_pai[i]
        x_mae[i], x_mae[index_mae] = x_mae[index_mae], x_mae[i]

        index_pai = y_pai.index(y_mae[i])
        index_mae = y_mae.index(y_pai[i])
        y_pai[i], y_pai[index_pai] = y_pai[index_pai], y_pai[i]
        y_mae[i], y_mae[index_mae] = y_mae[index_mae], y_mae[i]

    filho1 = list(zip(x_pai, y_pai))
    filho2 = list(zip(x_mae, y_mae))
    return filho1, filho2


def mutacao(alocacao):
    idx1, idx2 = random.sample(range(len(alocacao)), 2)

    aluno_a1, aluno_b1 = alocacao[idx1]
    aluno_a2, aluno_b2 = alocacao[idx2]

    alocacao[idx1] = (aluno_a1, aluno_b2)
    alocacao[idx2] = (aluno_a2, aluno_b1)


def resolver(matriz_alocacao, matriz_escola_a, matriz_escola_b, chance_mutacao):
    losses = funcao_heuristica(matriz_alocacao, matriz_escola_a, matriz_escola_b)
    new_matriz = copy.deepcopy(matriz_alocacao)

    melhor = elitismo(matriz_alocacao, losses)
    new_matriz[0] = melhor
    um = torneio(matriz_alocacao, losses)
    new_matriz[1] = um

    for i in range(2, 10, 2):
        pai = torneio(matriz_alocacao, losses)
        mae = torneio(matriz_alocacao, losses)
        f1, f2 = crossover(pai, mae)
        new_matriz[i] = f1
        new_matriz[i + 1] = f2

    for i in range(1, len(new_matriz)):
        if chance_mutacao > random.uniform(0, 1):
            mutacao(new_matriz[i])

    return new_matriz


if __name__ == "__main__":
    geracaoes = 10
    print("Geração 0:")
    mostrar(
        matriz_alocacao,
        funcao_heuristica(matriz_alocacao, matriz_escola_a, matriz_escola_b),
    )
    for i in range(1, geracaoes):
        matriz = resolver(matriz_alocacao, matriz_escola_a, matriz_escola_b, 0.10)
        print(f"Geração {i}:")
        mostrar(matriz, funcao_heuristica(matriz, matriz_escola_a, matriz_escola_b))
        print()
        matriz_alocacao = matriz
