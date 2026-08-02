import time

import numpy as np

# 1. Our raw data arrays.
# In the final library, we will load these from massive text files.
first_names = np.array(["Kashan", "Sarah", "Mudassar", "Alex", "Jordan"])
last_names = np.array(["Haider", "Hakkim", "Awan", "Smith", "Doe"])

print("Starting generation...")
start_time = time.time()

# 2. The Vectorized Magic
# We tell numpy to randomly pick 100,000 items from our arrays.
# It does this mathematically in C under the hood, bypassing slow Python loops.
random_firsts = np.random.choice(first_names, size=100000)
random_lasts = np.random.choice(last_names, size=100000)

# 3. Vectorized Concatenation
# Instead of looping to combine "First + Space + Last",
# np.char.add joins the entire arrays together all at once.
full_names = np.char.add(np.char.add(random_firsts, " "), random_lasts)

end_time = time.time()

# 4. Show the results
print(f"✅ Generated 100,000 names in: {end_time - start_time:.5f} seconds")
print(f"Sample output: {full_names[:5]}")
