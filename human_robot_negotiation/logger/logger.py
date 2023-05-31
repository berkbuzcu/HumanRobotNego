# coding=utf-8

import pandas as pd


class Logger:
    def __init__(
        self, participant_name, agent_type, interaction_type, log_file_path, domain
    ):
        self.participant_name = participant_name
        self.agent_type = agent_type
        self.interaction_type = interaction_type
        self.log_file_path = log_file_path
        self.domain = domain

    def log_negotiation_summary(
        self,
        session_number,
        emotion_counts,
        sens_dict,
        human_awareness,
        total_offers,
        time_passed,
        agent_score,
        user_score,
        is_agreement,
    ):
        d1 = {
            "Name": self.participant_name,
            "Total Bid": total_offers,
            "Agent Type": self.agent_type,
            "Interaction Type": self.interaction_type,
            "Scaled Time": time_passed,
            "Is Agreement": is_agreement,
            "Agent Score": agent_score,
            "User Score": user_score,
            "Frustrated": emotion_counts["Frustrated"],
            "Annoyed": emotion_counts["Annoyed"],
            "Dissatisfied": emotion_counts["Dissatisfied"],
            "Neutral": emotion_counts["Neutral"],
            "Convinced": emotion_counts["Convinced"],
            "Content": emotion_counts["Content"],
            "Worried": emotion_counts["Worried"],
            "Silent": sens_dict["silent"],
            "Nice": sens_dict["nice"],
            "Fortunate": sens_dict["fortunate"],
            "Unfortunate": sens_dict["unfortunate"],
            "Concession": sens_dict["concession"],
            "Selfish": sens_dict["selfish"],
            "Awareness": human_awareness,
            "Domain": self.domain,
        }

        df1 = pd.DataFrame(
            data=d1,
            index=[0],
            columns=[
                "Name",
                "Domain",
                "Agent Type",
                "Interaction Type",
                "Is Agreement",
                "Scaled Time",
                "Agent Score",
                "User Score",
                "Total Bid",
                "Awareness",
                "Silent",
                "Nice",
                "Fortunate",
                "Unfortunate",
                "Concession",
                "Selfish",
                "Frustrated",
                "Annoyed",
                "Dissatisfied",
                "Neutral",
                "Convinced",
                "Content",
                "Worried",
            ],
        )
        self.append_df_to_excel(
            f"{self.log_file_path + self.participant_name}_{session_number}_negotiation_summary.xlsx",
            df1,
            sheet_name="Negotiation Summary",
            index=False,
        )

    def log_offer_history(self, session_number, offer_df_list):
        result = pd.concat(offer_df_list)
        self.append_df_to_excel(
            f"{self.log_file_path + self.participant_name}_{session_number}_negotiation_logs.xlsx",
            result,
            sheet_name="Session " + str(session_number),
        )

    def append_df_to_excel(
        self, filename, df: pd.DataFrame, sheet_name="Sheet1", startrow=None, **to_excel_kwargs
    ):
        df.to_excel(filename, sheet_name=sheet_name)
