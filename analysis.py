import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

surveyHeaders = {
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
    stats['congestion_rating'] = (
        survey[surveyHeaders['congestion']].mean().round(2)
    )

    # REGION
    stats['region'] = survey[surveyHeaders['region']].value_counts().to_dict()

    # FREQUENCY
    stats['frequency'] = (
        survey[surveyHeaders['frequency']].value_counts().to_dict()
    )

    # ENTRY MODES
    stats['entry_modes'] = {
        'car': survey[surveyHeaders['car']],
        'bus': survey[surveyHeaders['bus']],
        'train': survey[surveyHeaders['train']],
        'bike': survey[surveyHeaders['bike']],
        'walk': survey[surveyHeaders['walk']],
    }

    # REASONS
    stats['reason'] = {
        'work': survey[surveyHeaders['work']],
        'kids': survey[surveyHeaders['kids']],
        'pleasure': survey[surveyHeaders['pleasure']],
        'other': survey[surveyHeaders['other_reason']],
    }

    # SUPPORT
    stats['support'] = (
        survey[surveyHeaders['support']].value_counts().to_dict().items()
    )
    # PRICE
    # sort by price by keys
    stats['price'] = survey[surveyHeaders['price']]

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
                        for k, v in stats['support']
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


def calculateCorrelations(stats, printStats=True):
    pass


def calculateElasticity(base_demand, priceData):
    def getPercentAbovePrice(price):
        return sum([priceData[p] for p in priceData if p > price]) / total

    total = sum(priceData.values())
    prices = list(range(10))
    return prices, [base_demand * getPercentAbovePrice(p) for p in prices]


def main():
    days = readCarData()
    survey = pd.read_csv('data/init-survey.csv')
    stats = surveyStats(survey, printStats=True)

    fig, ax = plt.subplots()

    base_demand = sum(days[0]['total_count'])
    regions = list(stats['region'].keys()) + ['All']

    for r in regions:
        priceData = {
            k: v
            for k, v in survey[surveyHeaders['price']][
                survey[surveyHeaders['region']] == r or r == 'All'
            ]
            .value_counts()
            .to_dict()
            .items()
            if k != 0
        }
        if not priceData:
            continue

        prices, demand = calculateElasticity(base_demand, priceData)

        ax.plot(demand, prices, label=r)

    ax.set_ylabel('Price (€)')
    ax.set_xlabel('Quantity (Cars)')
    ax.set_title('Price Elasticity of Demand')

    ax.legend()
    plt.show()


if __name__ == '__main__':
    main()
