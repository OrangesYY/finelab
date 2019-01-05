from qqbot import _bot as bot


class qqGroupSender:
    def init(self, qq_number):
        bot.Login(["-q", "3423392178"])
    def search_group_by_name(self, group_name):
        groups = bot.List("group", "NCU电赛基地2018招新群")
        self.group = groups[0]

    def send_message(self, message):
        bot.SendTo(self.group, message)

