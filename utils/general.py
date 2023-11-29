# decodifica le stringhe (ad esempio in state['message'])
def decode(X):
    return bytes(X).decode('utf-8').rstrip('\x00')