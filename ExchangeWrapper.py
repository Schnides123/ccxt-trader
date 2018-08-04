class ExchangeWrapper:

    def __init__(self, name, key, secret):
        self.Name = name
        self.Key = key
        self.Secret = secret

    def __str__(self):
        return self.Name
