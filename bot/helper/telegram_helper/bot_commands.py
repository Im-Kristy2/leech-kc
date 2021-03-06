from bot import CMD_INDEX


class _BotCommands:
    def __init__(self):
        self.StartCommand = f'start{CMD_INDEX}'
        self.MirrorCommand = f'mirror22{CMD_INDEX}'
        self.UnzipMirrorCommand = f'unzi2pmirror{CMD_INDEX}'
        self.ZipMirrorCommand = f'zipmirr2or{CMD_INDEX}'
        self.CancelMirror = f'cancel{CMD_INDEX}'
        self.CancelAllCommand = f'cancelall{CMD_INDEX}'
        self.ListCommand = f'list2{CMD_INDEX}'
        self.SearchCommand = f'sea2rch{CMD_INDEX}'
        self.StatusCommand = f'status{CMD_INDEX}'
        self.AuthorizedUsersCommand = f'users{CMD_INDEX}'
        self.AuthorizeCommand = f'authorize{CMD_INDEX}'
        self.UnAuthorizeCommand = f'unauthorize{CMD_INDEX}'
        self.AddSudoCommand = f'addsudo{CMD_INDEX}'
        self.RmSudoCommand = f'rmsudo{CMD_INDEX}'
        self.PingCommand = f'ping{CMD_INDEX}'
        self.RestartCommand = f'rs2{CMD_INDEX}'
        self.StatsCommand = f'stats2{CMD_INDEX}'
        self.HelpCommand = f'he2lp{CMD_INDEX}'
        self.LogCommand = f'log{CMD_INDEX}'
        self.CloneCommand = f'cl2one{CMD_INDEX}'
        self.CountCommand = f'cou2nt{CMD_INDEX}'
        self.WatchCommand = f'watc2h{CMD_INDEX}'
        self.ZipWatchCommand = f'zi2pwatch{CMD_INDEX}'
        self.QbMirrorCommand = f'qbmi2rror{CMD_INDEX}'
        self.QbUnzipMirrorCommand = f'q2bunzipmirror{CMD_INDEX}'
        self.QbZipMirrorCommand = f'qbzi2pmirror{CMD_INDEX}'
        self.DeleteCommand = f'del2{CMD_INDEX}'
        self.ShellCommand = f'shel2l{CMD_INDEX}'
        self.ExecHelpCommand = f'ex2echelp{CMD_INDEX}'
        self.LeechSetCommand = f'uploadas{CMD_INDEX}'
        self.SetThumbCommand = f'savethumb{CMD_INDEX}'
        self.LeechCommand = f'leech2{CMD_INDEX}'
        self.UnzipLeechCommand = f'leechunzip2{CMD_INDEX}'
        self.ZipLeechCommand = f'zipleech{CMD_INDEX}'
        self.QbLeechCommand = f'leechqb{CMD_INDEX}'
        self.QbUnzipLeechCommand = f'qbunzipleech{CMD_INDEX}'
        self.QbZipLeechCommand = f'qbzipleech{CMD_INDEX}'
        self.LeechWatchCommand = f'ytleech{CMD_INDEX}'
        self.LeechZipWatchCommand = f'leechzipwatch{CMD_INDEX}'
        self.RssListCommand = f'rsslist{CMD_INDEX}'
        self.RssGetCommand = f'rssget{CMD_INDEX}'
        self.RssSubCommand = f'rsssub{CMD_INDEX}'
        self.RssUnSubCommand = f'rssunsub{CMD_INDEX}'
        self.RssSettingsCommand = f'rssset{CMD_INDEX}'

BotCommands = _BotCommands()
