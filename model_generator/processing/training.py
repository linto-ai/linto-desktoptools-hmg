class TrainingSession:
    def __init__(self, model, initialEpoch: int = 0):
        self.model = model
        self.epoch = initialEpoch
        self.targetEpoch = self.epoch
    
    def stopTraining(self):
        self.model.stop_training = True


