from solver_agent import SolverAgent
from queuelib.queue_manager import MultiQueueHandler
from corelib.utility_space import UtilitySpace

# init_message:

# utility_space -> JSON
# time_controller -> think about this
# action_factory -> corelib

''' 
init agent messsage:
{
utilitySpace: JSON
domain type: 
}
'''

queue_handler = MultiQueueHandler(["agent", "logger"])
init_message = queue_handler.wait_for_message_from_queue("agent")

agent = SolverAgent()


