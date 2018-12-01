


from qqbot import _bot as bot
bot.Login(['-q','3423392178'])
groups = bot.List('group','NCU电赛基地2018招新群')
group = groups[0]
bot.SendTo(group,'bot_sent')