import pickle


def save_data_to_file(filename, data, io):
    with open(filename, 'wb') as file:
        pickle.dump(data, file)
    io.print(f'Data saved to {filename} successfully.')


def load_data_from_file(filename, io):
    try:
        with open(filename, 'rb') as file:
            data = pickle.load(file)
        io.print(f'Data loaded from {filename} successfully.')
        return data
    except FileNotFoundError as e:
        raise FileNotFoundError(f'File {filename} not found.') from e
