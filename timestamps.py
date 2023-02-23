import csv

headers = ['time', 'howth_count', 'sutton_count']
fileName = 'data/test-m.csv'

startH = 7
endH = 9
startM = 0
endM = 45

with open(fileName, 'w') as f:
    writer = csv.writer(f)
    # write header
    writer.writerow(headers)
    # write timestamps from 7:00 to 9:45 in 5 min increments
    # stop at 9:40
    for hour in range(startH, endH + 1):
        for minute in range(0, endM if hour == endH else 60, 5):
            writer.writerow([f'{hour}:{minute:02}', 0, 0])
