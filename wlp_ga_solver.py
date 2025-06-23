import pandas as pd
import random
import copy

def read_wlp_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    n, m = map(int, lines[0].split())
    capacities = list(map(float, lines[1].split()))
    setup_costs = list(map(float, lines[2].split()))
    # Müşteri taleplerini satır satır topla (bir satırda birden fazla değer olabilir)
    demands = []
    idx = 3
    while len(demands) < m:
        demands += list(map(float, lines[idx].split()))
        idx += 1
    # Taşıma maliyetlerini oku
    transport_costs = []
    for i in range(m):
        transport_costs.append(list(map(float, lines[idx].split())))
        idx += 1
    return n, m, capacities, setup_costs, demands, transport_costs

def calculate_fitness(assignments, n, m, capacities, setup_costs, demands, transport_costs):
    used_capacity = [0] * n
    used_warehouses = set()
    total_cost = 0
    for c in range(m):
        w = assignments[c]
        if w < 0 or w >= n:
            return float('inf')
        used_capacity[w] += demands[c]
        if used_capacity[w] > capacities[w]:
            return float('inf')
        used_warehouses.add(w)
        total_cost += transport_costs[c][w]
    for w in used_warehouses:
        total_cost += setup_costs[w]
    return total_cost

def create_individual(n, m, capacities, demands):
    # Her müşteri için rastgele kapasiteyi aşmayacak depo ata
    assignments = [-1] * m
    used_capacity = [0] * n
    for c in range(m):
        possible = [w for w in range(n) if used_capacity[w] + demands[c] <= capacities[w]]
        if not possible:
            assignments[c] = random.randint(0, n-1)  # Geçersiz atama, cezalandırılır
        else:
            w = random.choice(possible)
            assignments[c] = w
            used_capacity[w] += demands[c]
    return assignments

def mutate(assignments, n, m, capacities, demands, mutation_rate=0.1):
    new_assignments = assignments[:]
    used_capacity = [0] * n
    for c in range(m):
        used_capacity[new_assignments[c]] += demands[c]
    for c in range(m):
        if random.random() < mutation_rate:
            old_w = new_assignments[c]
            used_capacity[old_w] -= demands[c]
            possible = [w for w in range(n) if used_capacity[w] + demands[c] <= capacities[w]]
            if possible:
                new_w = random.choice(possible)
                new_assignments[c] = new_w
                used_capacity[new_w] += demands[c]
            else:
                new_assignments[c] = old_w
                used_capacity[old_w] += demands[c]
    return new_assignments

def crossover(parent1, parent2, n, m, capacities, demands):
    # Tek noktalı crossover
    point = random.randint(1, m-1)
    child = parent1[:point] + parent2[point:]
    # Kapasiteyi kontrol et, gerekirse düzelt
    used_capacity = [0] * n
    for c in range(m):
        w = child[c]
        used_capacity[w] += demands[c]
    for c in range(m):
        w = child[c]
        if used_capacity[w] > capacities[w]:
            # Kapasiteyi aşan depoya atanmışsa, uygun bir depo bul
            possible = [ww for ww in range(n) if used_capacity[ww] + demands[c] <= capacities[ww]]
            if possible:
                used_capacity[w] -= demands[c]
                new_w = random.choice(possible)
                child[c] = new_w
                used_capacity[new_w] += demands[c]
    return child

def genetic_algorithm(n, m, capacities, setup_costs, demands, transport_costs, pop_size=50, generations=200, mutation_rate=0.1):
    population = [create_individual(n, m, capacities, demands) for _ in range(pop_size)]
    best_solution = None
    best_cost = float('inf')
    for gen in range(generations):
        fitnesses = [calculate_fitness(ind, n, m, capacities, setup_costs, demands, transport_costs) for ind in population]
        # Elitizm
        best_idx = min(range(pop_size), key=lambda i: fitnesses[i])
        if fitnesses[best_idx] < best_cost:
            best_cost = fitnesses[best_idx]
            best_solution = population[best_idx][:]
        # Seçim (turnuva)
        new_population = [population[best_idx][:]]
        while len(new_population) < pop_size:
            i1, i2 = random.sample(range(pop_size), 2)
            parent1 = population[i1] if fitnesses[i1] < fitnesses[i2] else population[i2]
            i3, i4 = random.sample(range(pop_size), 2)
            parent2 = population[i3] if fitnesses[i3] < fitnesses[i4] else population[i4]
            child = crossover(parent1, parent2, n, m, capacities, demands)
            child = mutate(child, n, m, capacities, demands, mutation_rate)
            new_population.append(child)
        population = new_population
    return best_cost, best_solution

def main():
    results = []
    for size in [25, 50, 200, 300, 500]:
        filename = f"test_{size}.txt"
        n, m, capacities, setup_costs, demands, transport_costs = read_wlp_file(filename)
        cost, assignments = genetic_algorithm(n, m, capacities, setup_costs, demands, transport_costs)
        if cost == float('inf') or assignments is None:
            print(f"{filename}: Geçerli çözüm bulunamadı!")
            results.append({"Dosya Boyutu": size, "Optimal Maliyet": None, "Atama": ""})
        else:
            print(f"{filename}: Optimal Maliyet: {cost:.2f}")
            print("Atama:", " ".join(map(str, assignments)))
            results.append({"Dosya Boyutu": size, "Optimal Maliyet": cost, "Atama": " ".join(map(str, assignments))})
    # Excel'e yaz
    df = pd.DataFrame(results)
    df.to_excel("WLP_sonuclar.xlsx", index=False)
    print("Sonuçlar WLP_sonuclar.xlsx dosyasına kaydedildi.")

if __name__ == "__main__":
    main()
