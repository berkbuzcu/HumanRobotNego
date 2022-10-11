# coding=utf-8


class SensitivityCalculator:
    """
    Örnek olarak bizim domain üzerinden yapıyorum -> 4 issue var.
    Her issue için 5 farklı değer(value) var.
    """

    def get_opponent_moves_list(
        self,
        exp_opp_issue_weights,
        exp_opp_value_weights,
        opponent_bids,
        agent_bid_utility_list,
    ):
        # Opponentın bid utilitylerini tutacağım liste.
        opp_bid_utility_list = []
        # Opp bidleri iterate ediyorum.
        for opponent_bid in opponent_bids:
            # Bidin utilitysini initialize ediyorum.
            opp_bid_utility = 0
            # Bid için issueları iterate ediyorum.
            for issue_index, issue in enumerate(opponent_bid):
                # Issue index kullanarak issue weightini alıyorum -> [1, 3, 2, 4]te mesela 1'in issue indexi 0 -> issue_weights[0]
                # Issue'yu kullanarak value weightini alıyorum. -> [ [0, 0.25, 0.5, 0.75, 1], [0, 0.25, 0.5, 0.75, 1], [0, 0.25, 0.5, 0.75, 1], [0, 0.25, 0.5, 0.75, 1] ]
                # issue_value[0][1] yaptığımda 0.25'i veriyor. Çarpınca utilityi elde ediyorum.
                opp_bid_utility += (
                    exp_opp_issue_weights[issue_index]
                    * exp_opp_value_weights[issue_index][issue]
                )
            # Burada bid utility'sini listeye ekliyorum move hesabı için.
            opp_bid_utility_list.append(opp_bid_utility)

        # Yukarıdaki işim bittikten sonra opponent'ın move listesini oluşturacağım.
        opp_move_list = []
        # Daha sonra tek tek opp ve bizim utility listelerimizi iterate ederek moveları hesaplıyorum.
        for i in range(len(opp_bid_utility_list) - 1):
            # Daha sonra move tipini seçiyorum bizim ve karşının utility farklarına bakarak.
            if (
                abs(opp_bid_utility_list[i + 1] - opp_bid_utility_list[i]) == 0
                and abs(agent_bid_utility_list[i + 1] - agent_bid_utility_list[i]) == 0
            ):
                opp_move_list.append("silent")
            elif (
                abs(opp_bid_utility_list[i + 1] - opp_bid_utility_list[i]) == 0
                and agent_bid_utility_list[i + 1] - agent_bid_utility_list[i] > 0
            ):
                opp_move_list.append("nice")
            elif (
                opp_bid_utility_list[i + 1] - opp_bid_utility_list[i] > 0
                and agent_bid_utility_list[i + 1] - agent_bid_utility_list[i] > 0
            ):
                opp_move_list.append("fortunate")
            elif (
                opp_bid_utility_list[i + 1] - opp_bid_utility_list[i] < 0
                and agent_bid_utility_list[i + 1] - agent_bid_utility_list[i] < 0
            ):
                opp_move_list.append("unfortunate")
            elif (
                opp_bid_utility_list[i + 1] - opp_bid_utility_list[i] < 0
                and agent_bid_utility_list[i + 1] - agent_bid_utility_list[i] > 0
            ):
                opp_move_list.append("concession")
            else:
                opp_move_list.append("selfish")

        # En son move listesini dönüyorum.
        return opp_move_list

    def get_sensitivity_rate(self, move_list):
        # Sensitivity için dict kullanıyorum.
        sensitivity_rate_dict = {
            "silent": 0,
            "nice": 0,
            "fortunate": 0,
            "unfortunate": 0,
            "concession": 0,
            "selfish": 0,
        }
        # Her move'u iterate ediyorum.
        for move in move_list:
            # Sensitivity dict'indeki sayısını 1 / toplam_move_sayısı kadar arttırıyorum o move'un.
            sensitivity_rate_dict[move] += 1.0 / len(move_list)
        # Dict'i dönüyorum.
        return sensitivity_rate_dict

    def get_opponent_awareness(
        self,
        exp_opp_issue_weights,
        exp_opp_value_weights,
        opponent_bids,
        agent_bid_utility_list,
    ):
        """
        Baştaki kısım move hesabıyla aynı zaten yukarı atabiliriz demiştim de, Onur böyle istedi :D
        """
        # Opponentın bid utilitylerini tutacağım liste.
        opp_bid_utility_list = []
        # Opp bidleri iterate ediyorum.
        for opponent_bid in opponent_bids:
            # Bidin utilitysini initialize ediyorum.
            opp_bid_utility = 0
            # Bid için issueları iterate ediyorum.
            for issue_index, issue in enumerate(opponent_bid):
                # Issue index kullanarak issue weightini alıyorum -> [1, 3, 2, 4]te mesela 1'in issue indexi 0 -> issue_weights[0]
                # Issue'yu kullanarak value weightini alıyorum. -> [ [0, 0.25, 0.5, 0.75, 1], [0, 0.25, 0.5, 0.75, 1], [0, 0.25, 0.5, 0.75, 1], [0, 0.25, 0.5, 0.75, 1] ]
                # issue_value[0][1] yaptığımda 0.25'i veriyor. Çarpınca utilityi elde ediyorum.
                opp_bid_utility += (
                    exp_opp_issue_weights[issue_index]
                    * exp_opp_value_weights[issue_index][issue]
                )
            # Burada bid utility'sini listeye ekliyorum awareness hesabı için.
            opp_bid_utility_list.append(opp_bid_utility)

        # Opponent awarenessı initialize ediyorum.
        opp_awareness = 0
        # Daha sonra tek tek opp ve bizim utility listelerimizi iterate ederek awarenessı hesaplıyorum.
        for i in range(len(opp_bid_utility_list) - 1):
            if (
                opp_bid_utility_list[i + 1] - opp_bid_utility_list[i] != 0
                and agent_bid_utility_list[i + 1] - agent_bid_utility_list[i] != 0
            ):
                # Eğer bir şeyler değişmiş ise, 1 / move_sayısı kadar awarenessı arttırıyorum.
                opp_awareness += 1.0 / (len(opp_bid_utility_list) - 1)

        return opp_awareness

    def get_sensitivity_class():
        # TODO: Burayı siz karar verin :D
        pass


if __name__ == "__main__":
    sc = SensitivityCalculator()
    # Örnek olarak issue weightlerini giriyorum.
    issue_weight_list = [0.48, 0.32, 0.16, 0.4]
    # Her issue için value değerlerini giriyorum.
    value_weight_list = [
        [0, 0.25, 0.5, 0.75, 1],
        [0, 0.25, 0.5, 0.75, 1],
        [0, 0.25, 0.5, 0.75, 1],
        [0, 0.25, 0.5, 0.75, 1],
    ]
    # Örnek opponent bidleri giriyorum.
    opp_bids = [[1, 3, 2, 4], [3, 2, 1, 3], [0, 2, 1, 4]]
    # Örnek bizim agentın bid utilityleri giriyorum, burada direk bidler de kullanılabilir karar verirsiniz.
    agent_bid_utilities = [60, 70, 58]
    # Opponent Move listi alıyorum.
    opponent_move_list = sc.get_opponent_moves_list(
        issue_weight_list, value_weight_list, opp_bids, agent_bid_utilities
    )
    print("Opponent move list:", opponent_move_list)
    # Opponent için sensitivity rate'i alıyorum.
    opponent_sensitivity_rates = sc.get_sensitivity_rate(opponent_move_list)
    print("Opponent sensitivity rates:", opponent_sensitivity_rates)
    # Opponent için awareness'ı alıyorum.
    opponent_awareness = sc.get_opponent_awareness(
        issue_weight_list, value_weight_list, opp_bids, agent_bid_utilities
    )
    print("Opponent awareness:", opponent_awareness)
