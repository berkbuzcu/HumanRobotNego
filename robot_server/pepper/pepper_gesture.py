class PepperGesture:
    def __init__(self):
        self.folder_path = "lnae-0a4161/Pepper 2/"
        # Set mood counts for agent.1
        self.num_of_moods = {
            "Frustrated": 0,
            "Annoyed": 0,
            "Dissatisfied": 0,
            "Neutral": 0,
            "Convinced": 0,
            "Content": 0,
            "Worried": 0,
        }

        self.files_by_mood = {
            "Annoyed": [
                "annoyed_1",
                "annoyed_3",
                "annoyed_2",
            ],
            "Frustrated": [
                "frustrated_1",
            ],
            "Dissatisfied": [
                "dissatisfied_1",
                "dissatisfied_3",
                "dissatisfied_2",
                "dissatisfied_4",
            ],
            "Neutral": ["thinking"], # Missing
            "Convinced": ["convinced_1", "convinced_2"],
            "Content": ["content_1", "content_2"],
            "Worried": [], # Missing
        }
        self.animations={
            "annoyed_1":"No, It is not acceptable!",
            "annoyed_3":"I wish you did not make this offer.",
            "annoyed_2":"That's so disappointing!",
            "frustrated_1":"Do you really think that is a fair offer? It is not acceptable at all.",
            "dissatisfied_1":"No, I can not accept that unfortunately.",
            "dissatisfied_3":"Sorry, I can not accept that.",
            "dissatisfied_2":"That is not going to work for me!",
            "dissatisfied_4":"I'm sorry but I could not agree to your offer. ",
            "thinking":"Hmm",
            "convinced_1":" Let me think about it. It is getting better but not enough.",
            "convinced_2":" I appreciate your offer. It would be great if you concede a little bit more. ",
            "content_1":"It is getting better but not enough.",
            "content_2":"That sounds good but you can give me a little bit more.",
        }

    def get_gesture(self, mood):
        """
        This function gets offer of the opponent's and lower threshold of the current tactic as input.
        Return robot mood and mood method to call and updates mood counts.
        """

        self.num_of_moods[mood] += 1

        res = self.num_of_moods[mood] % len(self.files_by_mood[mood])
        
        mood_file_idx = res if res != 0 else 1
        
        mood_file = mood.lower() + "_%s" % mood_file_idx
        mood_file=str("^start(")+str(self.folder_path + mood_file + "/behavior_1")+str(")")+self.animations[mood_file]
        # Return the robot action.
        return mood_file
