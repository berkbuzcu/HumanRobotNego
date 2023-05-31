class PepperGesture:
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
            "Content": ["content_1", "content_2", "content_3"],
            "Worried": [], # Missing
        }

    def get_gesture(self, mood):
        """
        This function gets offer of the opponent's and lower threshold of the current tactic as input.
        Return robot mood and mood method to call and updates mood counts.
        """

        self.num_of_moods[mood] += 1

        mood_file_idx = self.num_of_moods[mood] % len(self.files_by_mood[mood])
        mood_file = mood.lower() + "_%s" % mood_file_idx

        # Return the robot action.
        return mood_file
