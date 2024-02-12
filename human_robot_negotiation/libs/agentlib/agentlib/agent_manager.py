import json

from .abstract_agent import AbstractAgent
from queuelib.queue_manager import MultiQueueHandler, prep_init_message
from queuelib.enums import HANTQueue

''' 
init agent messsage:
{
utilitySpace: JSON
domain type: 
}
'''

'''
msg structure:

"from":
"body":


'''


class AgentManager:
    agent: AbstractAgent

    def __init__(self, agent_name, agent_class: AbstractAgent.__class__):
        self.agent = agent_class()
        self.agent.name = agent_name

        self.queue_handler = MultiQueueHandler([HANTQueue.AGENT.value, HANTQueue.LOGGER.value])
        self.queue_handler.send_message(HANTQueue.AGENT.value, prep_init_message(agent_name))

        self.start_agent()

    def start_agent(self):
        while True:
            message = self.queue_handler.wait_for_message_from_queue(HANTQueue.AGENT.value)

            print("SOLVER: ", message)
            # init - bid - termination
            message_body = message["body"]
            message_from = message["from"]
            message_type = message["type"]

            print(self.agent.name, ": MESSAGE RECEIVED FROM: ", message_from)

            if message_type == "init":
                self.agent._init_negotiation(message_body["utility_space"], message_body["domain_info"])
                reply = {
                    "from": self.agent.__class__.name,
                    "to": "core",
                    "type": "init",
                    "body": "",
                    "status": "success",
                }
                self.queue_handler.send_message(HANTQueue.AGENT.value, json.dumps(reply))

            ###
            if message_type == "bid":
                ## returns offer, agent mood
                offer, agent_mood = self.agent._receive_offer(message_body["offer"],
                                                              message_body["predictions"],
                                                              message_body["normalized_predictions"])
                reply = {
                    "from": self.agent.__class__.name,
                    "to": "core",
                    "type": "offer",
                    "body": {"offer": offer, "agent_mood": agent_mood},
                    "status": "success",
                }
                self.queue_handler.send_message(HANTQueue.AGENT.value, json.dumps(reply))


            if message_type == "termination":
                self.agent._negotiation_over(message_body["participant_name"],
                                             message_body["session_number"],
                                             message_body["termination_type"])

                reply = {
                    "from": self.agent.__class__.name,
                    "to": "core",
                    "type": "termination",
                    "body": "",
                    "status": "success",
                }

                self.queue_handler.send_message(HANTQueue.AGENT.value, json.dumps(reply))
                break
