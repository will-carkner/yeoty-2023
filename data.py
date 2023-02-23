import csv

headers = ['time', 'howth_count', 'sutton_count']
with open('data/thurs-m.csv', 'w') as f:
    writer = csv.writer(f)
    # write header
    writer.writerow(headers)
    # write timestamps from 7:00 to 9:45 in 5 min increments
    for hour in range(7, 10):
        for minute in range(0, 60, 5):
            writer.writerow([f'{hour}:{minute:02}', 0, 0])
