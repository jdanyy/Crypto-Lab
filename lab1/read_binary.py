import pickle

with open('res/decoded_binary.txt', 'rb') as f:
    binary_data = pickle.load(f)
    print(binary_data)
    
    
    