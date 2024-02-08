from .solver_agent import SolverAgent
from queuelib.queue_manager import MultiQueueHandler
from corelib.utility_space import UtilitySpace
from agentlib.agent_manager import AgentManager
import json

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

manager = AgentManager("Solver", SolverAgent)
manager.start_agent()
