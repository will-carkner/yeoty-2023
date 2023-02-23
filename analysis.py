import matplotlib.pyplot as plt
import pandas as pd


def readData():
    files = ['thurs-m.csv']
    data = []
    for fn in files:
        tData = pd.read_csv(f'data/{fn}')
        tData['time'] = pd.to_datetime(tData['time'])
        tData = tData.set_index('time')
        data.append(tData)
    return data


data = readData()

# plot data
fig, ax = plt.subplots()
ax.plot(data[0].index, data[0]['howth_count'], label='Howth')
ax.plot(data[0].index, data[0]['sutton_count'], label='Sutton')
ax.set_xlabel('Time')
ax.set_ylabel('Count')
ax.set_title('Vehicle Count')
ax.legend()
plt.show()
