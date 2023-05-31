from human_robot_negotiation.HANT.hant import HANT
hant = HANT()
hant.exec()

#import execnet
#from human_robot_negotiation import ROBOT_SERVER_DIR
#from robot_server import robot_runner
#
#
#python_exe = str(ROBOT_SERVER_DIR / f".venv_Nao" / "Scripts" / "python.exe")
#venvPath=f"popen//python={python_exe}"
#gw = execnet.makegateway(venvPath)
#
#channel = gw.remote_exec(robot_runner)
#channel.send("server;init_robot;nao")
#
#print("aaa: ", channel.receive())
