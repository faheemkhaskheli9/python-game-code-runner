# Example submission: allowed imports, prints, and plain computation.
# Represents the kind of code a learner writes to drive the Phase 2 game API.
import math
import random

random.seed(7)

path = []
x, y = 0, 0
for _ in range(5):
    step = random.choice(["N", "E", "S", "W"])
    if step == "N":
        y += 1
    elif step == "S":
        y -= 1
    elif step == "E":
        x += 1
    else:
        x -= 1
    path.append(step)

distance = round(math.hypot(x, y), 3)
print("moves:", " ".join(path))
print("final position:", (x, y))
print("distance from origin:", distance)
