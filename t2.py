import random
import math
import copy
import sys
from pathlib import Path

caminho = Path(sys.argv[1])


matriz_escola_a = []
matriz_escola_b = []

with open(caminho, "r") as f:
    n = int(f.readline())
    for i in range(n):
        matriz_escola_a.append(list(map(int, f.readline().split()[1:])))
    for i in range(n):
        matriz_escola_b.append(list(map(int, f.readline().split()[1:])))

rank_a = [[0] * (n + 1) for _ in range(n)]
rank_b = [[0] * (n + 1) for _ in range(n)]

for i in range(n):
    for j, aluno in enumerate(matriz_escola_a[i]):
        rank_a[i][aluno] = j

for i in range(n):
    for j, aluno in enumerate(matriz_escola_b[i]):
        rank_b[i][aluno] = j


tamanho_populacao = n * 75


matriz_alocacao = []
for _ in range(tamanho_populacao):
    alocacao = []
    for i in range(n):
        a = list(range(1, n + 1))
        b = list(range(1, n + 1))

        random.shuffle(a)
        random.shuffle(b)

        alocacao = list(zip(a, b))
    matriz_alocacao.append(alocacao)


def funcao_heuristica(matriz_alocacao, rank_a, rank_b):
    losses = []
    for alocacao in matriz_alocacao:
        loss = 0
        for aluno_a, aluno_b in alocacao:
            loss += rank_a[aluno_a - 1][aluno_b]
            loss += rank_b[aluno_b - 1][aluno_a]
        losses.append(loss)
    return losses


def mostrar(matriz_alocacao, losses):
    print()
    for individuo, loss in zip(matriz_alocacao, losses):
        print(individuo, loss)


def elitismo(matriz_alocacao, losses):
    index = losses.index(min(losses))

    return copy.deepcopy(matriz_alocacao[index])


def torneio(matriz_alocacao, losses):
    k = max(2, int(0.05 * tamanho_populacao))

    indices = random.sample(range(tamanho_populacao), k)

    melhor = min(indices, key=lambda i: losses[i])

    return matriz_alocacao[melhor].copy()


def crossover(pai, mae):
    """
    Crossover baseado em matching (herda casais).

    Cada indivíduo representa uma bijeção entre os alunos da escola A e da
    escola B, isto é, um conjunto de pares (A,B).

    O objetivo deste crossover é preservar esses pares bons

    Funcionamento:

    1) Todos os casais presentes nos DOIS pais são copiados diretamente para o
       filho. Como ambos os pais concordam nesses pares, eles provavelmente
       representam boas soluções.

    2) Para os demais alunos da escola A:
          - escolhe aleatoriamente entre o parceiro do pai e da mãe;
          - se esse parceiro ainda estiver livre, ele é utilizado;
          - caso contrário, tenta utilizar o parceiro do outro pai;
          - se ambos já estiverem ocupados, esse aluno fica pendente.

    3) Após percorrer todos os alunos, alguns parceiros da escola B ainda
       estarão livres. Eles são distribuídos aleatoriamente entre os alunos
       pendentes.
    """

    mapa_pai = dict(pai)
    mapa_mae = dict(mae)

    filho = {}
    usados_b = set()

    for a in range(1, n + 1):
        if mapa_pai[a] == mapa_mae[a]:
            filho[a] = mapa_pai[a]
            usados_b.add(mapa_pai[a])

    pendentes = []

    for a in range(1, n + 1):
        if a in filho:
            continue

        b_pai = mapa_pai[a]
        b_mae = mapa_mae[a]

        if random.random() < 0.5:
            primeira, segunda = b_pai, b_mae
        else:
            primeira, segunda = b_mae, b_pai

        if primeira not in usados_b:
            filho[a] = primeira
            usados_b.add(primeira)

        elif segunda not in usados_b:
            filho[a] = segunda
            usados_b.add(segunda)

        else:
            pendentes.append(a)

    livres = [b for b in range(1, n + 1) if b not in usados_b]
    random.shuffle(livres)

    for a, b in zip(pendentes, livres):
        filho[a] = b

    return sorted(filho.items()), sorted(filho.items())


def mutacao(alocacao):
    idx1, idx2 = random.sample(range(len(alocacao)), 2)

    aluno_a1, aluno_b1 = alocacao[idx1]
    aluno_a2, aluno_b2 = alocacao[idx2]

    alocacao[idx1] = (aluno_a1, aluno_b2)
    alocacao[idx2] = (aluno_a2, aluno_b1)


def resolver(matriz_alocacao, rank_a, rank_b, chance_mutacao):
    losses = funcao_heuristica(matriz_alocacao, rank_a, rank_b)
    new_matriz = copy.deepcopy(matriz_alocacao)

    melhor = elitismo(matriz_alocacao, losses)
    new_matriz[0] = melhor
    um = torneio(matriz_alocacao, losses)
    new_matriz[1] = um

    for i in range(2, tamanho_populacao, 2):
        pai = torneio(matriz_alocacao, losses)
        mae = torneio(matriz_alocacao, losses)
        f1, f2 = crossover(pai, mae)
        new_matriz[i] = f1
        new_matriz[i + 1] = f2

    for i in range(1, len(new_matriz)):
        if chance_mutacao > random.uniform(0, 1):
            mutacao(new_matriz[i])

    return new_matriz


def avaliacao(losses):
    """
    Retorna a porcentagem da população que é igual ao melhor
    """
    melhor = min(losses)
    return sum(loss == melhor for loss in losses) / len(losses)


if __name__ == "__main__":
    taxa_mutacao = 0.05
    termo_parar = n * 5

    try:
        pausar = sys.argv[2] == "pausado"
    except:
        pausar = False

    try:
        printar = sys.argv[3] != "sem_print"
    except:
        printar = True

    i = 0
    geracoes_sem_melhoria = 0
    ultimo_melhor_resultado = math.inf

    print("Geração 0:")
    if printar:
        mostrar(
            matriz_alocacao,
            funcao_heuristica(matriz_alocacao, rank_a, rank_b),
        )

    if pausar:
        input()

    while True:
        matriz = resolver(matriz_alocacao, rank_a, rank_b, taxa_mutacao)
        print(f"Geração {i}:")
        losses = funcao_heuristica(matriz, rank_a, rank_b)

        menor_loss = min(losses)
        if printar:
            mostrar(matriz, losses)
        else:
            print(menor_loss, avaliacao(losses))
        print()

        if menor_loss < ultimo_melhor_resultado:
            ultimo_melhor_resultado = menor_loss
            geracoes_sem_melhoria = 0
        else:
            geracoes_sem_melhoria += 1
        convergencia = avaliacao(losses)
        if geracoes_sem_melhoria >= termo_parar and convergencia > max(
            1 - 1.2 * taxa_mutacao, 1 / tamanho_populacao
        ):
            print(convergencia)
            print(elitismo(matriz_alocacao, losses), menor_loss)
            break

        matriz_alocacao = matriz
        if pausar:
            input()
        i += 1
