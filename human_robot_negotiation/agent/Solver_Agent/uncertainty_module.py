#from HANT.utility_space import UtilitySpace
#from agent.Solver_Agent.ComparisonObject import ComparisonObject

from human_robot_negotiation.agent.solver_agent.comparison_object import ComparisonObject
from human_robot_negotiation.HANT.utility_space import UtilitySpace

import typing as t
import copy


class UncertaintyModule:
    def __init__(self, utility_space: UtilitySpace):
        self.utility_space = utility_space

    def estimate_opponent_preferences(self, opponentOfferHistory):
        """
        This method takes opponent's bidding history and returns estimated utility_space of the opponent.
        """

        # Dictionary that keeps number of same values as keys, and compared offers list as values.
        comparablesDict = {}

        for i in range(len(opponentOfferHistory)):
            for j in range(i + 1, len(opponentOfferHistory)):
                # Compare current and next bid's issue values. If they are same, add to the list.
                # same_values_indices = [
                #    a
                #    for (a, b) in zip(
                #        opponentOfferHistory[i].get_bid(),
                #        opponentOfferHistory[j].get_bid())
                #    if a == b
                # ]
                # Keep number of values that are same.
                #sameValueCount = len(same_values_indices)
                # If count does not exist, create new empty list to append later on.
                # if sameValueCount not in comparablesDict:
                #    comparablesDict[sameValueCount] = []
                # Create comparison variable for history offers.
                comparision_pair = ComparisonObject(
                    opponentOfferHistory[i].get_bid(),
                    opponentOfferHistory[j].get_bid()
                )
                # Check if this pair already exists in dict, append otherwise with same value count as a key
                # REVISIT: sameValueCount != comparing counts (should be issuesize-comparing issues if dont work)
                comparing_issues_size = comparision_pair.comparing_issues_size
                # If count does not exist, create new empty list to append later on.
                if comparing_issues_size not in comparablesDict:
                    comparablesDict[comparing_issues_size] = []

                if comparision_pair not in comparablesDict[comparing_issues_size]:
                    comparablesDict[comparing_issues_size].append(
                        comparision_pair)

        # List that keeps importance of the issues in descending order.
        # idx 0 is more important than idx 1
        # Initially at semi-random (the order which the values were inserted)
        issues_orderings = self.utility_space.issue_names.copy()
        value_orderings: t.Dict[str, t.List[str]] = self.utility_space.issue_values_list.copy()
        issue_size = len(issues_orderings)

        all_pairwise_comparisons = {key: [] for key in issues_orderings}
        # "issue_name": (first_value, second_value)
        ground_truths = []  # list of 1 value pairwise comparisons

        # comparison pair size 1 equals comparing only 1 value, the rest of the values are the same
        for comparison_item in comparablesDict.get(1, []):
            for (issue_name, first_value, second_value) in comparison_item:
                first_value_idx = value_orderings[issue_name].index(
                    first_value)
                second_value_idx = value_orderings[issue_name].index(
                    second_value)

                all_pairwise_comparisons[issue_name].append(
                    (first_value, second_value))
                ground_truths.append((first_value, second_value))

                value_orderings[issue_name][first_value_idx], value_orderings[issue_name][second_value_idx] = value_orderings[
                    issue_name][second_value_idx], value_orderings[issue_name][first_value_idx]

        for issue, ordering in value_orderings.items():
            for first_item, second_item in all_pairwise_comparisons[issue]:
                first_item_idx  = ordering.index(first_item)
                second_item_idx = ordering.index(second_item)

                if first_item_idx > second_item_idx:
                    ordering[first_item_idx], ordering[second_item_idx] = ordering[second_item_idx], ordering[first_item_idx]
                

        while True:
            prev_size = sum(map(len, all_pairwise_comparisons.values()))
            for comparing_amount in range(2, issue_size):
                list_of_comparisons = comparablesDict.get(comparing_amount, [])

                for comparison_item in list_of_comparisons:
                    conflicts = []
                    for (issue_name, first_value, second_value) in comparison_item:

                        # first condition: if the reverse of what is proposed by this comparison item
                        # (e.g., the first_value > second_value) see if it is contradicted by the ground truths.
                        # and ignore it.
                        if (second_value, first_value) in ground_truths:
                            continue
                        if (second_value, first_value) in all_pairwise_comparisons[issue_name]:
                            conflicts.append(issue_name)

                    # if issue_size = 4, and we are evaluation by pairs (comparing_amount = 2)
                    # then 4 - 2 - 1 = 1 conflicts means 1 conflicting value is enough to
                    # determine that one value is weighted higher than the rest.

                    if len(conflicts) == issue_size - comparing_amount - 1:
                        final_issues = [
                            issue for issue in issues_orderings if issue not in conflicts]

                        for issue in final_issues: ## buraya geri dön
                            if issue in comparison_item.comparing_issues:
                                if comparison_item[issue] in all_pairwise_comparisons[issue]:
                                    continue
                                all_pairwise_comparisons[issue].append(
                                    comparison_item[issue])

            if prev_size == sum(map(len, all_pairwise_comparisons.values())):
                break


        for issue, ordering in value_orderings.items():
            for first_item, second_item in all_pairwise_comparisons[issue]:
                first_item_idx  = ordering.index(first_item)
                second_item_idx = ordering.index(second_item)

                if first_item_idx > second_item_idx:
                    ordering[first_item_idx], ordering[second_item_idx] = ordering[second_item_idx], ordering[first_item_idx]
        
        # swap_code:

        # value_orderings[issue_name][first_value_idx], value_orderings[issue_name][second_value_idx] = value_orderings[
        #    issue_name][second_value_idx], value_orderings[issue_name][first_value_idx]
        # second phase is we evaluate and gather information on the rest of the comparison sizes

        ### OLD APPROACH FOR ISSUE EVAL###
        
        '''for comparing_issues_size, comparison_pair_list in comparablesDict.items():
            # FALSE previous assertion: If the same value number is 1, there is no information that we can gain.
            # Same value amount = 1 means there are i - 1 amounts to compare.
            # sameValueCount renamed to comparing_issues_size to fix this.s
            # For 1 amounts to compare, we acquire the most concrete,image.png baseline results given our opponent
            # concession assumption

            # We can skip 1's since we already acquired this information
            if comparing_issues_size == 1:
                continue

            for comparison_pair in comparison_pair_list:
                conftlicting_issues = []

                # for iss in comparison_pair.comparing_issues:
                #    first_value = comparison_pair.first_offer[iss]
                #    second_value = comparison_pair.second_offer[iss]

                #    if first_value < second_value:
                #        conftlicting_issues.append(iss)

                # custom iterator for comparison pair returns: (issue_name, first_offer_value, second_offer_value)
                for issue_name, first_value, second_value in comparison_pair:
                    first_value_idx = value_orderings[issue_name].index(
                        first_value)
                    second_value_idx = value_orderings[issue_name].index(
                        second_value)

                    # given the values are held in descending order, this is a conflict
                    # assumption #1: issue value is lower so it sets the first_value a lower value
                    if second_value_idx < first_value_idx:
                        conftlicting_issues.append(issue_name)

                if len(conftlicting_issues) > 0:
                    non_conflicting_issues = [issue_name for issue_name in self.utility_space.issue_names
                                              if issue_name not in conftlicting_issues]

                    # code block below swaps the issue ordering based on assumption #1.
                    # since conflicting issue is considered to be causing the lowness, it must be swapped with the non-conflicting comparing issues.
                    for conflict in conftlicting_issues:
                        for non_conflict in non_conflicting_issues:
                            non_conflict_idx = issues_orderings.index(
                                non_conflict)
                            conflict_idx = issues_orderings.index(conflict)

                            if non_conflict_idx < conflict_idx:
                                issues_orderings[non_conflict], issues_orderings[
                                    conflict] = issues_orderings[conflict], issues_orderings[non_conflict]'''

        conflict_count = {}

        for comparing_issues_size, comparison_pair_list in comparablesDict.items():
            for comparison_pair in comparison_pair_list:
                comparing_issues = comparison_pair.comparing_issues
                conflict_issues = []

                for issue_name, first_value, second_value in comparison_pair:
                    ordering_for_issue_values: t.List[str] = value_orderings.get(issue_name)

                    # given the values are held in descending order, this is a conflict
                    if (ordering_for_issue_values.index(str(second_value)) < ordering_for_issue_values.index(str(first_value))):
                        conflict_issues.append(issue_name)

                if len(conflict_issues) == comparing_issues_size - 1:
                    conflict_count[tuple(comparing_issues)] = conflict_count.get(
                        tuple(comparing_issues), 0) + 1

        # The conflicts are sorted by count, so the most count conflict will have the highest precedence
        # Since they are applied in order of their counts
        conflict_count_sorted_values = dict(
            sorted(conflict_count.items(), key=lambda item: item[1]))

        for conflict, amount in conflict_count_sorted_values.items():
            non_conflict_issues = [
                issue for issue in issues_orderings.copy() if issue not in conflict]

            # first_value is an earlier bid than second_value
            # the orderings are held in descending order
            # these conflicts are captured based on the fact that the first value is supposed to be higher
            # but they are actually not, therefore, the conflicting issues are the issues that should be
            # lower in value given our assumption of human concession in negotiations
            # code block below swaps the issue ordering based on above
            # since conflicting issue is considered to be causing the lowness, it must be swapped with the non-conflicting comparing issues.
            for conflict_issue in conflict:
                for non_conflict_issue in non_conflict_issues:
                    conflict_idx = issues_orderings.index(conflict_issue)
                    non_conflict_idx = issues_orderings.index(
                        non_conflict_issue)
                    if conflict_idx < non_conflict_idx:
                        issues_orderings[conflict_idx], issues_orderings[non_conflict_idx] = issues_orderings[
                            non_conflict_idx], issues_orderings[conflict_idx]

        issue_weights = [0.0] * issue_size
        issues_mid = (issue_size - 1) // 2
        diff = 1 / issue_size
        issue_weights[issues_mid] = diff
        sum_diffs = diff

        for i in range(1, issue_size // 2 + 1):
            target = issues_mid + i
            if target < issue_size:
                target_next = issue_weights[issues_mid + i - 1]
                diff = target_next + target_next / issue_size
                sum_diffs += diff
                issue_weights[target] = diff
            target = issues_mid - i
            if target < issue_size:
                target_prev = issue_weights[issues_mid - i + 1]
                diff = target_prev - target_prev / issue_size
                sum_diffs += diff
                issue_weights[target] = diff
        
        issue_weights = [issue / sum_diffs for issue in issue_weights]
        issue_weights.reverse()

        value_weights = {}
        for issue, values in value_orderings.items():
            expected = []
            for i in range(1, len(values) + 1):
                expected.append(i / len(values))
            
            #reverse this list to make sure the highest value is set from 1 ... 0
            expected.reverse()
            value_weights[issue] =  dict(zip(values, expected))

        estimated_opponent_preference = copy.deepcopy(self.utility_space)

        estimated_opponent_preference.issue_weights = dict(zip(issues_orderings, issue_weights))
        estimated_opponent_preference.issue_value_evaluation = value_weights

        #realOpponentPreference = UtilitySpace("HATN/Domain/Fruit/Fruits_A_Human.xml")

        # print("estimated weights:", estimatedOpponentPreference.issue_weights)
        # print("real weights:", realOpponentPreference.issue_weights)
        #
        #
        # print("Issue orderings:", issuesOrderings)
        #
        # ### RMSE ###
        # sum = 0
        # for opponentOffer in opponentOfferHistory:
        # 	#print("real utility and x:", realOpponentPreference.get_offer_utility(opponentOffer), opponentOffer.get_bid())
        # 	sum += (estimatedOpponentPreference.get_offer_utility(opponentOffer) - realOpponentPreference.get_offer_utility(opponentOffer)) ** 2
        #
        # print("estimated utility and x:", estimatedOpponentPreference.get_offer_utility(opponentOfferHistory[-1].get_bid()), opponentOfferHistory[-1].get_bid())
        # print("real utility and x:", realOpponentPreference.get_offer_utility(opponentOfferHistory[-1]), opponentOfferHistory[-1].get_bid())
        #
        # rmse_a = sum / len(opponentOfferHistory)
        # rmse_b = sqrt(rmse_a)
        #
        # print("RMSE: ", rmse_b)

        return estimated_opponent_preference