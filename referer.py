with open('./log.log', 'r') as f:
    logs = f.readlines()

for log in logs:
    if 'Referer' in log:
        print(log)
