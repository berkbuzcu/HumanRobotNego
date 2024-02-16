import json

from .abstract_agent import AbstractAgent
from queuelib.queue_manager import MultiQueueHandler, prep_init_message
from queuelib.enums import HANTQueue
from queuelib.message import AgentMessage

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

        self.queue_handler = MultiQueueHandler([HANTQueue.AGENT, HANTQueue.LOGGER], correlation_id=self.agent.name)
        self.queue_handler.send_message(prep_init_message(agent_name, HANTQueue.AGENT))

        self.start_agent()

    def start_agent(self):
        while True:
            message = self.queue_handler.wait_for_message_from_queue(HANTQueue.AGENT)

            print("SOLVER: ", message)
            # init - bid - termination
            message_from = message.sender

            message_payload = message.payload
            payload_context = message_payload["context"]

            print(self.agent.name, ": MESSAGE RECEIVED FROM: ", message_from)

            if payload_context == "init_negotiation":
                self.agent._init_negotiation(message_payload["utility_space"], message_payload["domain_info"])
                reply = {
                    "from": self.agent.__class__.name,
                    "to": "core",
                    "type": "init",
                    "body": "",
                    "status": "success",
                }
                reply_message = AgentMessage(self.agent.name, reply, True)
                self.queue_handler.send_message(reply_message)

            ###
            if payload_context == "receive_bid":
                offer, agent_mood = self.agent._receive_offer(message_payload["offer"],
                                                              message_payload["predictions"],
                                                              message_payload["normalized_predictions"])
                reply = {
                    "from": self.agent.__class__.name,
                    "to": "core",
                    "type": "offer",
                    "body": {"offer": offer, "agent_mood": agent_mood},
                    "status": "success",
                }
                reply_message = AgentMessage(self.agent.name, reply, True)
                self.queue_handler.send_message(reply_message)

            if payload_context == "termination":
                self.agent._negotiation_over(message_payload["participant_name"],
                                             message_payload["session_number"],
                                             message_payload["termination_type"])

                reply = {
                    "from": self.agent.__class__.name,
                    "to": "core",
                    "type": "termination",
                    "body": "",
                    "status": "success",
                }

                reply_message = AgentMessage(self.agent.name, reply, True)
                self.queue_handler.send_message(reply_message)
                break
