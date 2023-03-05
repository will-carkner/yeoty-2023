import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

warnings.filterwarnings('ignore')

sh = {
    # 'submissionid': 'Submission ID',
    # 'respon'Respondent ID',
    'timestamp': 'Submitted at',
    'email': 'What is your email address?',
    'region': 'What region do you live in?',
    # 'Untitled short answer field (1)',
    'frequency': 'How often do you enter Howth?',
    # 'How do you usually enter Howth?',
    'car': 'How do you usually enter Howth? (Car / Motorcycle)',
    'bus': 'How do you usually enter Howth? (Bus)',
    'train': 'How do you usually enter Howth? (Train)',
    'bike': 'How do you usually enter Howth? (Bike / Scooter)',
    'walk': 'How do you usually enter Howth? (Walk)',
    # 'Why do you usually make these journeys into Howth?',
    'work': 'Why do you usually make these journeys into Howth? (Work)',
    'kids': 'Why do you usually make these journeys into Howth? (Dropping off children for school)',
    'pleasure': 'Why do you usually make these journeys into Howth? (Tourism / Pleasure)',
    'other_reason': 'Why do you usually make these journeys into Howth? (Other)',
    # 'other_reason': 'Untitled short answer field (2)',
    'congestion': 'On a scale of 1-5, how big of an issue is congestion in Howth? (5 being the most)',
    'support': 'Would you support congestion pricing (a daily fee to enter by car, only at peak hours) in Howth, which would lower traffic and delays? (only for non-residents)',
    # 'Untitled short answer field (3)',
    'price': 'If congestion pricing was implemented, what is the maximum price (€) you would pay before stopping driving to enter Howth through Sutton Cross?',
    # 'Any other comments?',
}
regions = []


def readCarData():
    files = ['thurs-m.csv', 'thurs-a.csv']
    days = []
    for fn in files:
        cars = pd.read_csv(f'data/{fn}')
        cars['time'] = pd.to_datetime(cars['time'])
        cars = cars.set_index('time')
        cars['total_count'] = cars['howth_count'] + cars['sutton_count']
        days.append(cars)
    return days


def surveyStats(survey, printStats=True):
    stats = {}

    # CONGESTION
    stats['congestion_rating'] = survey[sh['congestion']].mean().round(2)

    # REGION
    stats['region'] = survey[sh['region']].value_counts().to_dict()

    # FREQUENCY
    stats['frequency'] = survey[sh['frequency']].value_counts().to_dict()

    # ENTRY MODES
    stats['entry_modes'] = {
        'car': survey[sh['car']],
        'bus': survey[sh['bus']],
        'train': survey[sh['train']],
        'bike': survey[sh['bike']],
        'walk': survey[sh['walk']],
    }

    # REASONS
    stats['reason'] = {
        'work': survey[sh['work']],
        'kids': survey[sh['kids']],
        'pleasure': survey[sh['pleasure']],
        'other': survey[sh['other_reason']],
    }

    # SUPPORT
    stats['support'] = survey[sh['support']].value_counts().to_dict()
    # PRICE
    # sort by price by keys
    stats['price'] = survey[sh['price']]

    if printStats:
        # make survey stats red
        print('\033[91mSURVEY STATS\033[0m', '-' * 20, sep='\n')
        output = [
            {'Congestion rating': stats['congestion_rating']},
            {
                'Region': ', '.join(
                    [
                        f'{k} ({round(v / len(survey) * 100, 2)}%)'
                        for k, v in stats['region'].items()
                    ]
                )
            },
            {
                'Frequency': ', '.join(
                    [
                        f'{k} ({round(v / len(survey) * 100, 2)}%)'
                        for k, v in stats['frequency'].items()
                    ]
                )
            },
            {
                'Entry modes': ', '.join(
                    [
                        f'{k} ({round(v.mean() * 100, 2)}%)'
                        for k, v in stats['entry_modes'].items()
                    ]
                )
            },
            {
                'Reason': ', '.join(
                    [
                        f'{k} ({round(v.mean() * 100, 2)}%)'
                        for k, v in stats['reason'].items()
                    ]
                )
            },
            {
                'Support': ', '.join(
                    [
                        f'{k} ({round(v / len(survey) * 100, 2)}%)'
                        for k, v in stats['support'].items()
                    ]
                )
            },
            {'Avg Price': stats['price'].mean().round(2)},
            {
                'Price distribution': ', '.join(
                    [
                        f'{k} ({round(v / len(survey) * 100, 2)}%)'
                        for k, v in sorted(
                            stats['price'].value_counts().to_dict().items()
                        )
                    ]
                )
            },
        ]

        for o in output:
            for k, v in o.items():
                print(f'\033[92m{k}\033[0m: \033[94m{v}\033[0m')

        print('-' * 20)
    return stats


def calculateElasticity(base_demand, priceData):
    def getPercentAbovePrice(price):
        return sum([priceData[p] for p in priceData if p > price]) / total

    total = sum(priceData.values())
    prices = list(range(10))
    return prices, [base_demand * getPercentAbovePrice(p) for p in prices]


def calculateCorrelations(survey, stats, printStats=True):
    cors = {}

    transport_modes = {
        'car': survey[sh['car']],
        'noCar': np.array(list(map(lambda x: not x, survey[sh['car']]))),
        'car+': np.array(
            list(
                map(
                    lambda x: x[0] and x[1],
                    zip(
                        survey[sh['car']],
                        survey[sh['bus']]
                        | survey[sh['train']]
                        | survey[sh['bike']]
                        | survey[sh['walk']],
                    ),
                )
            )
        ),
    }
    support = np.array(
        list(
            map(lambda x: True if x == 'Yes' else False, survey[sh['support']])
        )
    )
    frequency = np.array(
        list(
            map(
                lambda x: {
                    'Rarely or never': 1,
                    'Once a month': 2,
                    'Once a week': 3,
                    'A few times a week': 4,
                    'Every weekday': 5,
                    'Daily': 6,
                }[x],
                survey[sh['frequency']],
            )
        )
    )
    congestion = np.array(survey[sh['congestion']])
    prices = np.array(survey[sh['price']])
    reasons = {
        'work': survey[sh['work']].fillna(False),
        'kids': survey[sh['kids']].fillna(False),
        'pleasure': survey[sh['pleasure']].fillna(False),
        'otherReason': survey[sh['other_reason']].fillna(False),
    }

    for mode in transport_modes:
        cors[f'{mode}-support'] = np.corrcoef(transport_modes[mode], support)[
            0
        ][1]
        cors[f'{mode}-frequency'] = np.corrcoef(
            transport_modes[mode], frequency
        )[0][1]
        cors[f'{mode}-congestion'] = np.corrcoef(
            transport_modes[mode], congestion
        )[0][1]
        cors[f'{mode}-price'] = np.corrcoef(
            transport_modes[mode][prices > 0], prices[prices > 0]
        )[0][1]

    cors['congestion-support'] = np.corrcoef(congestion, support)[0][1]
    cors['congestion-price'] = np.corrcoef(
        congestion[prices > 0], prices[prices > 0]
    )[0][1]

    cors['frequency-congestion'] = np.corrcoef(frequency, congestion)[0][1]
    cors['frequency-support'] = np.corrcoef(frequency, support)[0][1]

    cors['support-price'] = np.corrcoef(
        support[prices > 0], prices[prices > 0]
    )[0][1]

    for r in regions:
        df = survey[sh['region']] == r
        cors[f'{r}-support'] = np.corrcoef(df, support)[0][1]
        cors[f'{r}-congestion'] = np.corrcoef(df, congestion)[0][1]
        cors[f'{r}-price'] = np.corrcoef(df[prices > 0], prices[prices > 0])[
            0
        ][1]
        cors[f'{r}-frequency'] = np.corrcoef(df, frequency)[0][1]
        for reason in reasons:
            cors[f'{r}-{reason}'] = (
                np.corrcoef(df, reasons[reason])[0][1]
                if r != 'Howth / Sutton'
                else np.float64('nan')
            )
        for mode in transport_modes:
            cors[f'{r}-{mode}'] = np.corrcoef(df, transport_modes[mode])[0][1]

    for reason in reasons:
        cors[f'{reason}-support'] = np.corrcoef(reasons[reason], support)[0][1]
        cors[f'{reason}-congestion'] = np.corrcoef(
            reasons[reason], congestion
        )[0][1]
        cors[f'{reason}-price'] = np.corrcoef(
            reasons[reason][prices > 0], prices[prices > 0]
        )[0][1]
        cors[f'{reason}-frequency'] = np.corrcoef(reasons[reason], frequency)[
            0
        ][1]
        for mode in transport_modes:
            cors[f'{reason}-{mode}'] = np.corrcoef(
                reasons[reason], transport_modes[mode]
            )[0][1]

    if printStats:
        print('\033[91mCORRELATIONS\033[0m', '-' * 20, sep='\n')
        output = [
            {
                f'{mode} - support': cors[f'{mode}-support'].round(2)
                for mode in transport_modes
            },
            {'-': '-'},
            {
                f'{mode} - frequency': cors[f'{mode}-frequency'].round(2)
                for mode in transport_modes
            },
            {'-': '-'},
            {
                f'{mode} - congestion': cors[f'{mode}-congestion'].round(2)
                for mode in transport_modes
            },
            {'-': '-'},
            {
                f'{mode} - price': cors[f'{mode}-price'].round(2)
                for mode in transport_modes
            },
            {'-': '-'},
            {'Congestion - support': cors['congestion-support'].round(2)},
            {'Congestion - price': cors['congestion-price'].round(2)},
            {'-': '-'},
            {'Frequency - congestion': cors['frequency-congestion'].round(2)},
            {'Frequency - support': cors['frequency-support'].round(2)},
            {'Support - price': cors['support-price'].round(2)},
            {'-': '-'},
            {f'{r} - support': cors[f'{r}-support'].round(2) for r in regions},
            {'-': '-'},
            {
                f'{r} - congestion': cors[f'{r}-congestion'].round(2)
                for r in regions
            },
            {'-': '-'},
            {f'{r} - price': cors[f'{r}-price'].round(2) for r in regions},
            {'-': '-'},
            {
                f'{r} - {reason}': cors[f'{r}-{reason}'].round(2)
                for r in regions
                for reason in reasons
            },
            {'-': '-'},
            {
                f'{r} - {mode}': cors[f'{r}-{mode}'].round(2)
                for r in regions
                for mode in transport_modes
            },
            {'-': '(frequency is inflated bc howth people will say daily)'},
            {
                f'{r} - frequency': cors[f'{r}-frequency'].round(2)
                for r in regions
            },
            {'-': '-'},
            {
                f'{reason} - support': cors[f'{reason}-support'].round(2)
                for reason in reasons
            },
            {'-': '-'},
            {
                f'{reason} - congestion': cors[f'{reason}-congestion'].round(2)
                for reason in reasons
            },
            {'-': '-'},
            {
                f'{reason} - price': cors[f'{reason}-price'].round(2)
                for reason in reasons
            },
            {'-': '-'},
            {
                f'{reason} - frequency': cors[f'{reason}-frequency'].round(2)
                for reason in reasons
            },
            {'-': '-'},
            {
                f'{reason} - {mode}': cors[f'{reason}-{mode}'].round(2)
                for reason in reasons
                for mode in transport_modes
            },
        ]
        for o in output:
            for k, v in o.items():
                print(f'\033[92m{k}\033[0m: \033[94m{v}\033[0m')

        print('-' * 20)


def main():
    global regions
    periods = readCarData()
    survey = pd.read_csv('data/init-survey.csv')

    stats = surveyStats(survey, printStats=True)
    regions = [
        r for r in list(stats['region'].keys()) if stats['region'][r] > 5
    ]

    cors = calculateCorrelations(survey, stats, printStats=True)

    # create a graph of morning days
    # for i, period in enumerate(periods):
    #     fig, ax = plt.subplots()
    #     # period = period.resample('10T').sum()
    #     # print(period)
    #     ax.plot(period['total_count'], label='Total')
    #     ax.set_ylabel('Cars')
    #     ax.set_xlabel('Time')
    #     ax.set_title('Morning Traffic' if i == 0 else 'Evening Traffic')
    # plt.show()

    # elasticity graph
    # fig, ax = plt.subplots()

    # base_demand = sum(periods[0]['total_count'])

    # for r in regions + ['All']:
    #     priceData = {
    #         k: v
    #         for k, v in (
    #             survey[sh['price']][survey[sh['region']] == r]
    #             if r != 'All'
    #             else survey[sh['price']]
    #         )
    #         .value_counts()
    #         .to_dict()
    #         .items()
    #         if k != 0
    #     }
    #     if not priceData:
    #         continue

    #     prices, demand = calculateElasticity(base_demand, priceData)

    #     ax.plot(demand, prices, label=r)

    # ax.set_ylabel('Price (€)')
    # ax.set_xlabel('Quantity (Cars)')
    # ax.set_title('Price Elasticity of Demand')

    # ax.legend()
    # plt.show()


if __name__ == '__main__':
    main()
