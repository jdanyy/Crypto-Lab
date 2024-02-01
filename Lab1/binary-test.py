import pickle

test_data = {'Dani': 21, 'Gyuri': 22, 'Janos': 41}

with open('res/binary.txt', 'wb') as f:
    pickle.dump(test_data, f)
    