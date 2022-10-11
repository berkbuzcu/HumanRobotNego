from xml.dom.minidom import parse
import xml.dom.minidom
import itertools
import math


class UtilitySpace:
    def __init__(self, profile_file):
        # Role of the agent.
        self.profile_file = profile_file
        # Role weights of the agent. {issuename: issueweight, ....} etc.
        self.issue_weights = {}
        # REMOVED: Name to index dict for issue. {"Apple": 0, "Banana": 1} etc.
        #self.issue_name_to_index = {}
        # REMOVED: Index to name dict for issue. {0: "Apple", 1: "Banana"} etc.
        #self.issue_index_to_name = {}
        # Issue's value evaluations.  { "Apple": {0: 0.3, 1: 0.2}, "Banana": {0: 0.2, 1: 0.7} } etc.
        self.issue_value_evaluation = {}
        # Keep every issue's values in a dictionary. NEW: {"Apple": ["0", "1", "2"...], "accomodation": ["Camp", "Tent"]}REMOVED: [ [0, 1, 2, 3], ["Antalya", "Izmir"] ] etc.
        self.issue_values_list = {}
        # Issue name list.
        self.issue_names = []
        # Issues max count list for each issue.
        self.issue_max_counts = {}
        # Call the role weight function for complete the weight dictionary.

        # SUB-SUB dictionary. ie: {"Apple": {"0": 0, "1", 0.25...}, "accomodation": {"hotel": 1, "tent": 0.75...}}

        self.__set_utility_space()
        # Generate all possible offers.
        self.grid = [[(str(key).title(), "black") for key in value_dict.keys()] for value_dict in self.issue_value_evaluation.values()]
        
        self.indices = {}
        for issue_idx, (issue, values) in enumerate(self.issue_value_evaluation.items()):
            for value_idx, value in enumerate(values):
                issue_value_key = f"{issue}_{value}"
                self.indices[issue_value_key] = (issue_idx, value_idx)

    # Read the xml file of weights of keywords, then add to dictionary for calculation purpose.
    def __set_utility_space(self):
        # Open XML document using minidom parser
        DOMTree = xml.dom.minidom.parse(self.profile_file)
        collection = DOMTree.documentElement
        # Get issue list from the preference profile.
        issue_list = collection.getElementsByTagName("issue")
        weight_list = collection.getElementsByTagName("weight")
        # Get weight of the keywords and append to role weights.
        for issue, weight in zip(issue_list, weight_list):
            issue_name = issue.attributes["name"].value.lower()
            issue_weight = weight.attributes["value"].value
            self.issue_max_counts[issue_name] = int(getattr(issue.attributes.get("max_count"), 'value', 0))
            self.issue_weights[issue_name] = float(issue_weight)
            self.issue_names.append(issue_name)
            value_eval_dict = {}
            issue_values = []
            for item in issue.getElementsByTagName("item"):
                item_value = item.getAttribute("value").lower()
                item_eval = item.getAttribute("evaluation")
                value_eval_dict[item_value] = float(item_eval)
                issue_values.append(item_value)
            self.issue_value_evaluation[issue_name] = value_eval_dict
            self.issue_values_list[issue_name] = issue_values

        self.issue_value_evaluation = {key: dict(sorted(value.items(), key=lambda item: item[1], reverse=True)) for key, value in self.issue_value_evaluation.items()}

    def calculate_offer_for_opponent(self, offer):
        opponent_offer = {}
        for issue_name, offered_amount in offer.items():
            # Get max count of the issue.
            issue_max_count = self.issue_max_counts[issue_name]
            # Calculate leftover for the opponent of iterating issue.
            left_count = issue_max_count - int(offered_amount)
            opponent_offer[issue_name] = str(left_count)
        return opponent_offer

    def get_domain_type(self):
        return self.domain_type

    def get_2d_ranked_grid_colored(self):
        return self.grid

    def get_value_coord(self, value):
        return self.indices[str(value)]

