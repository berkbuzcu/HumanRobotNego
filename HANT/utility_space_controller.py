from xml.dom.minidom import parse
import xml.dom.minidom
import itertools


class UtilitySpaceController:
    def __init__(self, domain_file):
        self.domain_name = ""
        # Role of the agent.
        self.domain_file = domain_file
        self.issue_values_list = {}
        self.issue_names = []

        # Call the role weight function for complete the weight dictionary.
        self.__set_utility_space()

    def __set_utility_space(self):
        # Open XML document using minidom parser
        DOMTree = xml.dom.minidom.parse(self.domain_file)
        collection = DOMTree.documentElement
        # Get issue list from the preference profile.
        utility_space_obj = collection.getElementsByTagName("utility_space")[0]
        self.domain_type = utility_space_obj.attributes["domain_type"].value
        self.domain_name = utility_space_obj.attributes["domain_name"].value
        
        issue_list = collection.getElementsByTagName("issue")
        weight_list = collection.getElementsByTagName("weight")
        # Get weight of the keywords and append to role weights.
        for issue, weight in zip(issue_list, weight_list):
            issue_name = issue.attributes["name"].value
            self.issue_names.append(issue_name)
            issue_values = []
            for item in issue.getElementsByTagName("item"):
                item_value = item.getAttribute("value")
                issue_values.append(item_value)
            self.issue_values_list[issue_name] = issue_values     

    # Gets the offer and calculates leftover items for opponent in resource allocation type domains.
    def calculate_offer_for_opponent(self, offer):
        opponent_offer = []
        for issue_name, offered_amount in offer.items():
            # Get max count of the issue.
            issue_max_count = self.issue_max_counts[issue_name]
            # Calculate leftover for the opponent of iterating issue.
            left_count = issue_max_count - int(offered_amount)
            opponent_offer.append(left_count)
        return opponent_offer

    def convert_offer_dict_to_list(self, offer_dict):
        offer_list = [None] * self.number_of_issues
        for (issue_name, issue_value) in offer_dict.items():
            issue_index = self.issue_name_to_index[issue_name]
            # Append to the offer list with amount.
            offer_list[issue_index] = issue_value
        return offer_list

    def get_domain_type(self):
        return self.domain_type
