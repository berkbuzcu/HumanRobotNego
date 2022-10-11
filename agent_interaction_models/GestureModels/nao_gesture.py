class NaoGestures:
    def __init__(self):
        # Set mood counts for agent.
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
                "annoyed_6",
                "annoyed_2",
                "annoyed_4",
                "annoyed_7",
                "annoyed_5",
            ],
            "Frustrated": [
                "frustrated_1",
                "frustrated_3",
                "frustrated_2",
                "frustrated_4",
            ],
            "Dissatisfied": [
                "dissatisfied_1",
                "dissatisfied_3",
                "dissatisfied_6",
                "dissatisfied_2",
                "dissatisfied_4",
                "dissatisfied_7",
                "dissatisfied_5",
                "dissatisfied_8",
            ],
            "Neutral": ["neutral_1", "neutral_2"],
            "Convinced": [
                "convinced_1",
                #"convinced_2",
                "convinced_3",
                "convinced_4",
            ],
            "Content": ["content_1", "content_2"],
            "Worried": ["worried_1", "worried_2", "worried_3"],
        }

    def get_gesture(self, mood):
        """
        This function gets offer of the opponent's and lower threshold of the current tactic as input.
        Return robot mood and mood method to call and updates mood counts.
        """

        self.num_of_moods[mood] += 1

        mood_file_idx = (self.num_of_moods[mood] % (len(self.files_by_mood[mood]) - 1 )) + 1
        mood_file = mood.lower() + "_%s" % mood_file_idx

        # Return the robot action.
        return mood_file
