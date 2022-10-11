import execnet
from robot_client import RobotClient

gw = execnet.makegateway("popen//python=D:\PythonProjects\Human-Robot-Nego\AgentInteractionModels\.venv\Scripts\python.exe")
channel = gw.remote_exec("""
                            from AgentInteractionModels.robot_server import RobotServer
                            robot_server = RobotServer(channel)
                            robot_server.start_server()
                        """)

robot_client = RobotClient(channel)
robot_client.send_init_robot("nao")
robot_client.send_mood("Frustrated")


channel.close()