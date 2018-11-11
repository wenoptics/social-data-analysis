class Article:

    def __init__(self, id_, grade=''):
        self.__grade = grade
        self.id_ = id_

    @property
    def grade(self):
        return self.__grade.upper()
