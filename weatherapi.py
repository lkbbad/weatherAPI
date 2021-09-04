import requests
import numpy as np
from datetime import datetime
from datetime import timedelta
from datetime import date
import csv
import statistics

K = 273.15

###############################################################################

'''
Function that converts the current block's date text to a datetime object.
'''
def get_dt_tm(dt_str):
    dt_tm = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    
    #  Offset by the timezone offset to get local time, not UTC time
    tz_offset = data['city']['timezone']
    dt_tm = dt_tm + timedelta( seconds=tz_offset)
    return(dt_tm)
'''
Function that convert temperature lists to numpy arrays and finds the max and min.
'''
def get_max_min(temp_maxs, temp_mins):
    temp_maxs_array = np.array(temp_maxs) 
    temp_mins_array = np.array(temp_mins)
    max_maxs = np.amax(temp_maxs_array)
    min_mins = np.amin(temp_mins_array)
    return(max_maxs, min_mins)

'''
Function that appends the max and min temps to lists for that day.
'''
def append_max_min(max, min, temp_maxs, temp_mins):
    temp_maxs.append(max)
    temp_mins.append(min)
    return(temp_maxs, temp_mins)

###############################################################################

states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

###############################################################################

api_key = 'XXXXXX'
loc = [
    ['Anchorage', 'Alaska', 'USA'],
    ['Chennai', 'India'],
    ['Jiangbei', 'China'],
    ['Kathmandu', 'Nepal'],
    ['Kothagudem', 'India'],
    ['Lima','Peru'],
    ['Manhasset','New York', 'USA'],
    ['Mexico City','Mexico'],
    ['Nanaimo','Canada'],
    ['Peterhead','Scotland'],
    ['Polevskoy','Russia'],
    ['Round Rock','Texas', 'USA'],
    ['Seoul','South Korea'],
    ['Solihull', 'England'],
    ['Tel Aviv', 'Israel']
]

f = open('temp.csv', 'w')
writer = csv.writer(f)
writer.writerow(['City','Min 1','Max 1','Min 2','Max 2','Min 3','Max 3','Min 4','Max 4','Min 5','Max 5','Min Avg','Max Avg'])

for i in loc:
    URL = 'https://api.openweathermap.org/data/2.5/forecast?'
    city = i[0]
    country = i[1]
    if country in states.values():
        country = "USA"
    URL = URL + 'q=' + city + ',' + country + '&appid=' + api_key

    response = requests.get(URL)
    if response.status_code == 200:      # Success
        data = response.json()
        
        #  Get OUR current date in Raleigh, NC, USA
        cur_dt = date.today()

        #  Search for the first block that starts tomorrow
        first = 0
        for i in range(0, len(data['list'])):
            #  Convert the current block's date text to a datetime object
            dt_str = data['list'][i]['dt_txt']
            dt_tm = get_dt_tm(dt_str)

            #  If our day is the same as the block's day, the block is for today and NOT tomorrow, so keep searching. Otherwise, break out of the loop
            if cur_dt.day != dt_tm.day:
                first = i
                cur_dt = dt_tm
                break

        temp_maxs = [] 
        temp_mins = []
        day_dict_mins = {}
        day_dict_maxs = {}
        day_count = 0
        # Starting from the first block for tomorrow, iterate through all blocks
        for j in range(first, len( data['list'])):
            dt_str = data['list'][j]['dt_txt']
            dt_tm = get_dt_tm(dt_str)

            # If the there are leftover blocks at the end:
            if day_count == 4 and len(temp_mins) == 8:
                day_count += 1
                max = data['list'][j]['main']['temp_max']
                min = data['list'][j]['main']['temp_min']
                temp_maxs, temp_mins = append_max_min(max, min, temp_maxs, temp_mins)
                
                max_maxs, min_mins = get_max_min(temp_maxs, temp_mins)

                # add max and min for each day to dictionary as a value with the day number (1-5) as the key
                day_dict_mins.update({day_count : min_mins})
                day_dict_maxs.update({day_count : max_maxs})
                break

            num_blocks = len(data['list'])-1
            # Check if the current block is the last available block
            if j == num_blocks:
                day_count += 1
                max = data['list'][j]['main']['temp_max']
                min = data['list'][j]['main']['temp_min']
                temp_maxs, temp_mins = append_max_min(max, min, temp_maxs, temp_mins)

                max_maxs, min_mins = get_max_min(temp_maxs, temp_mins)

                # add max and min for each day to dictionary as a value with the day number (1-5) as the key
                day_dict_mins.update({day_count : min_mins})
                day_dict_maxs.update({day_count : max_maxs})
                break

            # For each block that is not the last block, check if the date matches the current day
            elif cur_dt.day == dt_tm.day:
                max = data['list'][j]['main']['temp_max']
                min = data['list'][j]['main']['temp_min']
                temp_maxs, temp_mins = append_max_min(max, min, temp_maxs, temp_mins)
    
            # If the date doesn't match the current day, it is for the next day
            else:
                day_count += 1
                max_maxs, min_mins = get_max_min(temp_maxs, temp_mins)

                # add max and min for each day to dictionary as a value with the day number (1-5) as the key
                day_dict_mins.update({day_count : min_mins})
                day_dict_maxs.update({day_count : max_maxs})
            
                # clear arrays of temperatures for use on the new day
                temp_maxs = []
                temp_mins = []

                # reset current date to the date of the new block
                cur_dt = dt_tm

                max = data['list'][j]['main']['temp_max']
                min = data['list'][j]['main']['temp_min']
                temp_maxs, temp_mins = append_max_min(max, min, temp_maxs, temp_mins)

        avg_max = statistics.mean(day_dict_maxs.values())
        avg_min = statistics.mean(day_dict_mins.values())

        writer.writerow([city + ", " + country, "{:.2f}".format(day_dict_mins[1]-K), "{:.2f}".format(day_dict_maxs[1]-K), 
            "{:.2f}".format(day_dict_mins[2]-K), "{:.2f}".format(day_dict_maxs[2]-K), 
            "{:.2f}".format(day_dict_mins[3]-K), "{:.2f}".format(day_dict_maxs[3]-K),
            "{:.2f}".format(day_dict_mins[4]-K), "{:.2f}".format(day_dict_maxs[4]-K),
            "{:.2f}".format(day_dict_mins[5]-K), "{:.2f}".format(day_dict_maxs[5]-K),
            "{:.2f}".format(avg_min-K), "{:.2f}".format(avg_max-K)])

    else:       # Failure
        print('Error:', response.status_code)

f.close()
