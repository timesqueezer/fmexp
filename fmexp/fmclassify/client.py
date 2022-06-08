import flwr as fl

from fmexp.fmclassify import FMClassifier


class FMFederatedClient(fl.client.NumPyClient):
    def __init__(self, mode='request'):
        self.fm_classifier = FMClassifier()
        self.fm_classifier.load_data(mode=mode)

    def get_properties(self, config):
        print('GET_PROPERTIES', config)

    def get_parameters(self):
        return self.fm_classifier.get_model_parameters()

    def set_parameters(self, parameters):
        return self.fm_classifier.set_model_parameters(parameters)

    def fit(self, parameters, config):
        self.set_parameters(parameters)

        self.fm_classifier.train_model()

        return self.get_model_parameters(), len(self.X_train), {}

    def evaluate(self, parameters, config):
        self.set_parameters(parameters)

        score = self.fm_classifier.test_model()

        return score, len(self.X_test), { 'accuracy': score }
