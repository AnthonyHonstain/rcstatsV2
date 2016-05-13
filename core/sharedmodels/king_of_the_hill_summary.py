

class KoHSummary():
    def __init__(
        self, 
        official_class_id, 
        official_class_name, 
        racerid__id, 
        racerid__racerpreferredname,
        score):

        self.official_class_id = official_class_id
        self.official_class_name = official_class_name
        self.racerid__id = racerid__id
        self.racerid__racerpreferredname = racerid__racerpreferredname
        self.score = score

    def __repr__(self):
        return '{} {} {} {} {}'.format(
            self.official_class_id,
            self.official_class_name,
            self.racerid__id,
            self.racerid__racerpreferredname,
            self.score)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
