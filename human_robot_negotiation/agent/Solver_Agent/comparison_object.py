class ComparisonObject:
    def __init__(self, first_offer, second_offer):
        self.comparing_issues = []
        self.first_offer, self.second_offer = self.reduce_elements(
            first_offer, second_offer
        )

        self.comparing_issues_size = len(self.comparing_issues)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.first_offer) + " > " + str(self.second_offer)

    def __eq__(self, other):
        """
        Takes comparison object as input as returns true if they are same otherwise false.
        """
        return (
            self.first_offer == other.first_offer
            and self.second_offer == other.second_offer
        )

    def __iter__(self):
        for i in set(self.first_offer).intersection(self.second_offer):
            yield (i,) + (self.first_offer[i], self.second_offer[i])

    def __getitem__(self, issue):
        return (self.first_offer[issue], self.second_offer[issue])

    def reduce_elements(self, first_offer, second_offer):  # fix this with lambdas
        a = {}
        b = {}
        #print(first_offer, second_offer)
        for key in first_offer.keys():
            if first_offer[key] != second_offer[key]:
                a[key] = first_offer[key]
                b[key] = second_offer[key]
                self.comparing_issues.append(key)

        if len(a) == 0:
            return first_offer, second_offer

        return a, b

    def is_comparable(self, other):
        return self.comparing_issues in other.comparing_issues