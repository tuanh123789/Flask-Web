mport requests

url = 'http://localhost:5000/cbresults'
r3 = requests.post(url,json={'age','overall','potential','defending','physic','defending_standing_tackle','defending_sliding_tackle','defending_marking',
                             'attacking_heading_accuracy','power_strength'})

print(r3.json())