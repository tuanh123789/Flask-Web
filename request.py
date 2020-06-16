import requests

url = 'http://localhost:5000/results'
r = requests.post(url,json={'age','overall','potential','pace','shooting','physic','attacking_finishing','attacking_heading_accuracy',
                            'movement_sprint_speed','movement_balance','power_shot_power'})

print(r.json())