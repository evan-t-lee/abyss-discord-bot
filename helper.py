
def create_server_data():
    new_server = {'settings': create_settings()}
    return new_server

# Will return default settings if none are supplied
def create_settings(*args):
    print(args)
    settings = [15, 30, 30]
    for i in range(len(args)):
        if args[i]:
            settings[i] = args[i]
    return {
        'points_to_win': settings[0],
        'rounds': settings[1],
        'round_time': settings[2]
    }

def has_invalid_args(*args):
    for i in range(len(args)):
        if args[i] != None:
            if args[i] <= 0:
                return True
            if i == 2 and not (10 <= args[i] <= 60):
                return True
    return False

def write_data(data):
    with open('data.pkl', 'wb') as f:
        pickle.dump(DATA, f)
