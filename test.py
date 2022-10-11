
#issue_size = 5
#
#issue_weights = [0] * issue_size
#issues_mid = (issue_size - 1) // 2
#diff = 1 / issue_size
#issue_weights[issues_mid] = diff
#sum_diffs = diff
#for i in range(1, issue_size // 2 + 1):
#    target = issues_mid + i
#    if target < issue_size:
#        target_next = issue_weights[issues_mid + i - 1]
#        diff = target_next + target_next / issue_size
#        sum_diffs += diff
#        issue_weights[target] = diff
#    target = issues_mid - i
#    if target < issue_size:
#        target_prev = issue_weights[issues_mid - i + 1]
#        diff = target_prev - target_prev / issue_size
#        sum_diffs += diff
#        issue_weights[target] = diff
#issue_weights = [issue / sum_diffs for issue in issue_weights]
#
#print(issue_weights)
#print(sum(issue_weights))


#import pandas as pd
#
#items = [{
#    "Bidder": "Berk",
#    "Agent Utility": 100,
#    "Human Utility": 100, 
#    "Offer": {"a": "b", "c": "d"},
#    "Scaled Time": 1
#}]
#
#print(pd.DataFrame(items))


#from tabnanny import check
#
#
#def check_acceptance(final_target_utility, human_offer_utility):
#    if final_target_utility < human_offer_utility:
#        my_prev_util = final_target_utility
#        #self.agent_history.append(self.action_factory.get_offer_below_utility(final_target_utility))
#
#        return True, (True, "Happy")
#    return False, ()
#
#a, b = check_acceptance(100, 50)


class A:
    def __init__(self, a) -> None:
        self.a = {"a": a}

    def __eq__(self, __o: object) -> bool:
        return self.a == __o.a

    def __hash__(self) -> int:
        return sum([hash(item) for item in self.a.values()])

items = [A(1), A(3)]

print(A(1) in items)

# { bid1: 0, bid2: 0 } dict[bid1]

items = {A(1): 1, A(2): 2}

print(items[A(2)])