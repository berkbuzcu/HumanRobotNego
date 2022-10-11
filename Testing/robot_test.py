from naoqi import ALProxy

NAO_IP = "169.254.45.244"
NAO_PORT = 9559

motion = ALProxy("ALMotion", NAO_IP, 9559)
tts = ALProxy("ALTextToSpeech", NAO_IP, 9559)
managerProxy = ALProxy("ALBehaviorManager", NAO_IP, 9559)
autonomousProxy = ALProxy("ALAutonomousLife", NAO_IP, 9559)


# autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
# autonomousProxy.setAutonomousAbilityEnabled("AutonomousBlinking", False)
# autonomousProxy.setAutonomousAbilityEnabled("BasicAwareness", False)
# autonomousProxy.setAutonomousAbilityEnabled("ListeningMovement", False)

# managerProxy.runBehavior("naobehaviorsprojectfolder-choregraphe-28-d4aa29/LetsStart-1")

# autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)
# autonomousProxy.setAutonomousAbilityEnabled("AutonomousBlinking", False)
# autonomousProxy.setAutonomousAbilityEnabled("BasicAwareness", False)
# autonomousProxy.setAutonomousAbilityEnabled("ListeningMovement", False)

#
# managerProxy.installBehavior("/home/nao/behaviors/")

# installed_names = managerProxy.getInstalledBehaviors()
# for name in installed_names:
#     if "naobehaviorsprojectfolder" in name:
# 	    print(name)

# managerProxy.runBehavior("letsstart-730c90/LetsStart")
# managerProxy.runBehavior("animations/Stand/Gestures/IDontKnow_1")
# managerProxy.runBehavior("leavingnego-43dcab/LeavingNego")


# managerProxy.runBehavior("invitevideobehavior-c1ea0b/InviteVideoBehavior")

# managerProxy.runBehavior("naobehaviorsprojectfolder-choregraphe-28-d4aa29/offended/behavior_1")
# managerProxy.runBehavior("standup-a650fd/StandUp")


# managerProxy.runBehavior("behaviors-1-0/behaviors/StandUp/StandUp")
# managerProxy.runBehavior("behaviors-1-0/behaviors/SitDown/SitDown")
# managerProxy.runBehavior("behaviors-1-0/behaviors/LetsStart/LetsStart")
# managerProxy.runBehavior("behaviors-1-0/behaviors/LeavingNego/LeavingNego")

# from Agent_Interaction_Models.robot_mobile_action import RobotMobileAction
#
# action = RobotMobileAction()
#
# action.neutral()

# tts.say("That's \\pau=10\\ all")

## VIRTUAL ONE

#

# managerProxy.runBehavior("behaviors-1-0/behaviors/SitDown/SitDown")


# Run full motions.

folder_path = "naobehaviorsprojectfolder-choregraphe-28-d4aa29/"

managerProxy.runBehavior(folder_path + "acceptingOffer")
