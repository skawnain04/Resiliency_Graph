import itertools

# Original set
original_set = {1, 2, 3}

# Resulting list to store subsets
subset_list = []

# Generate all non-empty subsets
for r in range(1, len(original_set) + 1):
    for combo in itertools.combinations(original_set, r):
        subset_list.append(set(combo))

# Print the subsets
for subset in subset_list:
    print(subset)
