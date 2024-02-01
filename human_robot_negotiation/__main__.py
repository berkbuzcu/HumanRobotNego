# import argparse
# import sys
#
# import human_robot_negotiation.gui.config_manager
#
# parser = argparse.ArgumentParser(
#                     prog='human_robot_negotiation',
#                     description='---description---',
#                     epilog='---epilog---')
#
# parser.add_argument('-t', '--type', choices=['qt', 'web'], default="qt")      # option that takes a value
# args = parser.parse_args()
#
# if args.type == "web":
#     raise NotImplementedError()
#
# else:
#     ...
#     #config_manager

from human_robot_negotiation.core.core import HANT

hant = HANT()
hant.exec()