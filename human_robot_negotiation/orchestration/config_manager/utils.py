import pathlib
import xml
import numpy as np
import minidom

from human_robot_negotiation import DOMAINS_DIR


def get_utility_space_json(profile_file):
    tree = xml.dom.minidom.parse(profile_file)
    collection = tree.documentElement

    issue_list = collection.getElementsByTagName("issue")
    weight_list = collection.getElementsByTagName("weight")

    issue_weights = {}
    issue_max_counts = {}
    issue_names = []

    issue_value_evaluation = {}
    issue_values_list = {}

    for issue, weight in zip(issue_list, weight_list):
        issue_name = issue.attributes["name"].value.lower()
        issue_weight = weight.attributes["value"].value

        issue_max_counts[issue_name] = int(getattr(issue.attributes.get("max_count"), 'value', 0))
        issue_weights[issue_name] = float(issue_weight)
        issue_names.append(issue_name)

        value_eval_dict = {}
        issue_values = []

        for item in issue.getElementsByTagName("item"):
            item_value = item.getAttribute("value").lower()
            item_eval = item.getAttribute("evaluation")
            value_eval_dict[item_value] = float(item_eval)
            issue_values.append(item_value)

        issue_value_evaluation[issue_name] = value_eval_dict
        issue_values_list[issue_name] = issue_values

    issue_value_evaluation = {key: dict(sorted(value.items(), key=lambda item: item[1], reverse=True)) for
                              key, value in issue_value_evaluation.items()}

    utility_space_json = {
        "issue_value_evaluation": issue_value_evaluation,
        "issue_weights": issue_weights,
        "issue_names": issue_names,
        "issue_max_counts": issue_max_counts,
    }

    return utility_space_json


def get_domain_info(domain_file: str) -> dict:
    DOMTree = xml.dom.minidom.parse(domain_file)
    collection = DOMTree.documentElement
    # Get issue list from the preference profile.
    utility_space_obj = collection.getElementsByTagName("utility_space")[0]

    domain_name = utility_space_obj.attributes["domain_name"].value
    domain_type = utility_space_obj.attributes["domain_type"].value

    issue_list = collection.getElementsByTagName("issue")

    issue_names = []
    issue_values_list = {}

    # Get weight of the keywords and append to role weights.
    for issue in issue_list:
        issue_name = issue.attributes["name"].value
        issue_names.append(issue_name)
        issue_values = []
        for item in issue.getElementsByTagName("item"):
            item_value = item.getAttribute("value")
            issue_values.append(item_value)
        issue_values_list[issue_name] = issue_values

    return {
        "domain_name": domain_name,
        "domain_type": domain_type,
        "issue_names": issue_names,
        "issue_values_list": issue_values_list,
    }

### NEED THEM ORDERED ACCORDING TO PREFERENCE > ###
def get_preferences(issues_ordered, issue_values_ordered):
    preference_dict = {}
    reversed_pref_dict = {}

    weight_sum = 0.

    issue_order_human = [i for i in range(len(issues_ordered))]
    issue_order_agent = issue_order_human.copy()

    for i in range(0, len(issue_order_human), 2):
        issue_order_agent[i], issue_order_agent[i + 1] = issue_order_agent[i + 1], issue_order_agent[i]

    for i in range(len(issues_ordered)):
        preference_dict[issues_ordered[i]] = {'weight': len(issues_ordered) - i}
        reversed_pref_dict[issues_ordered[i]] = {'weight': len(issues_ordered) - issue_order_agent[i]}

        weight_sum += i + 1

    for issue_name in issues_ordered:
        preference_dict[issue_name]["weight"] = np.round(
            preference_dict[issue_name]["weight"] / weight_sum * 100.) / 100.
        reversed_pref_dict[issue_name]["weight"] = np.round(
            reversed_pref_dict[issue_name]["weight"] / weight_sum * 100.) / 100.

    for i, issue_name in enumerate(issues_ordered):
        value_order_human = [j for j in range(len(issue_values_ordered[issue_name]))]
        value_order_agent = value_order_human.copy()
        value_order_agent[:len(value_order_human) // 2] = value_order_human[len(value_order_human) // 2:]
        if len(value_order_human) % 2 == 1:
            value_order_agent[len(value_order_human) // 2 + 1:] = value_order_human[:len(value_order_human) // 2]
        else:
            value_order_agent[len(value_order_human) // 2:] = value_order_human[:len(value_order_human) // 2]

        for j, value_name in enumerate(issue_values_ordered[issue_name]):
            preference_dict[issue_name][value_name] = len(issue_values_ordered[issue_name]) - j
            reversed_pref_dict[issue_name][value_name] = len(issue_values_ordered[issue_name]) - value_order_agent[j]

        for value_name in issue_values_ordered[issue_name]:
            preference_dict[issue_name][value_name] = np.round(
                preference_dict[issue_name][value_name] / len(issue_values_ordered[issue_name]) * 100.) / 100.
            reversed_pref_dict[issue_name][value_name] = np.round(
                reversed_pref_dict[issue_name][value_name] / len(issue_values_ordered[issue_name]) * 100.) / 100.

    return preference_dict, reversed_pref_dict


def create_preference_xml(domain_info: dict, negotiator_name: str, negotiator_type: str, preference_dict: dict):
    root = minidom.Document()
    xml = root.createElement('negotiation_domain')
    root.appendChild(xml)

    utility_space = root.createElement('utility_space')
    utility_space.setAttribute('domain_name', domain_info["domain_name"])
    utility_space.setAttribute('domain_type', domain_info["domain_type"])
    utility_space.setAttribute('number_of_issues', str(len(preference_dict)))

    xml.appendChild(utility_space)

    issue_index = 1
    for issue_name, values in preference_dict.items():
        issue_weight = values.pop("weight")

        issue_weight_element = root.createElement('weight')
        issue_weight_element.setAttribute('index', str(issue_index))
        issue_weight_element.setAttribute('value', str(issue_weight))

        utility_space.appendChild(issue_weight_element)

        issue_element = root.createElement('issue')
        issue_element.setAttribute('index', str(issue_index))
        issue_element.setAttribute('name', str(issue_name))

        utility_space.appendChild(issue_element)

        issue_index += 1

        value_index = 1
        for value_name, value_weight in values.items():
            value_element = root.createElement('item')
            value_element.setAttribute('index', str(value_index))
            value_element.setAttribute('value', str(value_name))
            value_element.setAttribute('evaluation', str(value_weight))

            issue_element.appendChild(value_element)
            value_index += 1

    xml_str = root.toprettyxml(indent="\t")

    file_dir = pathlib.Path(domain_info["path"]).parent

    import os
    if not os.path.exists(file_dir / negotiator_name):
        os.mkdir(file_dir / negotiator_name)

    file_dir = file_dir / negotiator_name

    with open(file_dir / f"/{negotiator_type}.xml", "w") as f:
        f.write(xml_str)
