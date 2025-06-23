import pandas as pd

def read_wlp_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    n, m = map(int, lines[0].split())
    capacities = list(map(float, lines[1].split()))
    setup_costs = list(map(float, lines[2].split()))
    demands = list(map(float, lines[3:3+m]))
    transport_costs = []
    for i in range(3+m, 3+m+m):
        transport_costs.append(list(map(float, lines[i].split())))
    return n, m, capacities, setup_costs, demands, transport_costs

def greedy_wlp(n, m, capacities, setup_costs, demands, transport_costs):
    # Her müşteriyi en ucuz (taşıma maliyeti + depo kurulum maliyeti/ilk müşteri) depoya atamaya çalış
    assignments = [-1] * m
    used_capacity = [0] * n
    used_warehouses = set()
    for c in range(m):
        best_cost = float('inf')
        best_w = -1
        for w in range(n):
            if used_capacity[w] + demands[c] <= capacities[w]:
                # İlk müşteri için kurulum maliyeti ekle, diğerleri için ekleme
                extra_cost = setup_costs[w] if w not in used_warehouses else 0
                cost = transport_costs[c][w] + extra_cost
                if cost < best_cost:
                    best_cost = cost
                    best_w = w
        if best_w == -1:
            return float('inf'), []  # Geçerli çözüm yok
        assignments[c] = best_w
        used_capacity[best_w] += demands[c]
        used_warehouses.add(best_w)
    # Toplam maliyet
    total_cost = 0
    used_warehouses = set(assignments)
    for w in used_warehouses:
        total_cost += setup_costs[w]
    for c in range(m):
        total_cost += transport_costs[c][assignments[c]]
    return total_cost, assignments

def main():
    results = []
    for size in [25, 50, 200, 300, 500]:
        filename = f"test_{size}.txt"
        n, m, capacities, setup_costs, demands, transport_costs = read_wlp_file(filename)
        cost, assignments = greedy_wlp(n, m, capacities, setup_costs, demands, transport_costs)
        if cost == float('inf'):
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