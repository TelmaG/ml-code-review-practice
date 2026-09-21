from collections import defaultdict, deque
import time

state = defaultdict(deque)


def add(event):
    user = event['user_id']
    now = time.time()
    state[user].append((now, event['amount']))
    while state[user] and now - state[user][0][0] > 3600:
        state[user].popleft()
    return sum(x[1] for x in state[user])
