from re import match as re_match, findall as re_findall	 
from threading import Thread, Event	
from time import time	
from math import ceil	
from html import escape	
from psutil import virtual_memory, cpu_percent, disk_usage	
from requests import head as rhead	
from urllib.request import urlopen	
from telegram import InlineKeyboardMarkup	
from telegram.ext import CallbackQueryHandler

from bot.helper.telegram_helper.bot_commands import BotCommands	
from bot import download_dict, download_dict_lock, STATUS_LIMIT, botStartTime, DOWNLOAD_DIR, dispatcher, OWNER_ID	
from bot.helper.telegram_helper.button_build import ButtonMaker

MAGNET_REGEX = r"magnet:\?xt=urn:btih:[a-zA-Z0-9]*"	

URL_REGEX = r"(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+"	

COUNT = 0	
PAGE_NO = 1	


class MirrorStatus:	
    STATUS_UPLOADING = "Uᴘʟᴏᴀᴅɪɴɢ...📥"	
    STATUS_DOWNLOADING = "Dᴏᴡɴʟᴏᴀᴅɪɴɢ...📥"	
    STATUS_CLONING = "Cʟᴏɴɪɴɢ...♻️"	
    STATUS_WAITING = "Qᴜᴇᴜᴇᴅ...📝"	
    STATUS_FAILED = "Fᴀɪʟᴇᴅ 🚫. Cʟᴇᴀɴɪɴɢ Dᴏᴡɴʟᴏᴀᴅ 🧹..."	
    STATUS_PAUSE = "Pᴀᴜꜱᴇᴅ...⭕️"	
    STATUS_ARCHIVING = "Aʀᴄʜɪᴠɪɴɢ...🔐"	
    STATUS_EXTRACTING = "Exᴛʀᴀᴄᴛɪɴɢ...📂"	
    STATUS_SPLITTING = "Sᴘʟɪᴛᴛɪɴɢ...✂️"	
    STATUS_CHECKING = "CʜᴇᴄᴋɪɴɢUᴘ...📝"	
    STATUS_SEEDING = "Sᴇᴇᴅɪɴɢ...🌧"	

SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']	


class setInterval:	
    def __init__(self, interval, action):	
        self.interval = interval	
        self.action = action	
        self.stopEvent = Event()	
        thread = Thread(target=self.__setInterval)	
        thread.start()	

    def __setInterval(self):	
        nextTime = time() + self.interval	
        while not self.stopEvent.wait(nextTime - time()):	
            nextTime += self.interval	
            self.action()	

    def cancel(self):	
        self.stopEvent.set()	

def get_readable_file_size(size_in_bytes) -> str:	
    if size_in_bytes is None:	
        return '0B'	
    index = 0	
    while size_in_bytes >= 1024:	
        size_in_bytes /= 1024	
        index += 1	
    try:	
        return f'{round(size_in_bytes, 2)}{SIZE_UNITS[index]}'	
    except IndexError:	
        return 'File too large'	

def getDownloadByGid(gid):	
    with download_dict_lock:	
        for dl in list(download_dict.values()):	
            status = dl.status()	
            if (	
                status	
                not in [	
                    MirrorStatus.STATUS_ARCHIVING,	
                    MirrorStatus.STATUS_EXTRACTING,	
                    MirrorStatus.STATUS_SPLITTING,	
                ]	
                and dl.gid() == gid	
            ):	
                return dl	
    return None	

def getAllDownload(req_status: str):	
    with download_dict_lock:	
        for dl in list(download_dict.values()):	
            status = dl.status()	
            if status not in [MirrorStatus.STATUS_ARCHIVING, MirrorStatus.STATUS_EXTRACTING, MirrorStatus.STATUS_SPLITTING] and dl:	
                if req_status == 'down' and (status not in [MirrorStatus.STATUS_SEEDING,	
                                                            MirrorStatus.STATUS_UPLOADING,	
                                                            MirrorStatus.STATUS_CLONING]):	
                    return dl	
                elif req_status == 'up' and status == MirrorStatus.STATUS_UPLOADING:	
                    return dl	
                elif req_status == 'clone' and status == MirrorStatus.STATUS_CLONING:	
                    return dl	
                elif req_status == 'seed' and status == MirrorStatus.STATUS_SEEDING:	
                    return dl	
                elif req_status == 'all':	
                    return dl	
    return None	

def get_progress_bar_string(status):	
    completed = status.processed_bytes() / 8	
    total = status.size_raw() / 8	
    p = 0 if total == 0 else round(completed * 100 / total)	
    p = min(max(p, 0), 100)	
    cFull = p // 8	
    p_str = '■' * cFull	
    p_str += '□' * (12 - cFull)	
    p_str = f"[{p_str}]"	
    return p_str	

def get_readable_message():	
    with download_dict_lock:
        msg = ""
        dlspeed_bytes = 0
        uldl_bytes = 0
        START = 0	
        num_active = 0	
        num_seeding = 0	
        num_upload = 0	
        for stats in list(download_dict.values()):	
            if stats.status() == MirrorStatus.STATUS_DOWNLOADING:	
               num_active += 1	
            if stats.status() == MirrorStatus.STATUS_UPLOADING:	
               num_upload += 1	
            if stats.status() == MirrorStatus.STATUS_SEEDING:	
               num_seeding += 1	
        if STATUS_LIMIT is not None:	
            tasks = len(download_dict)	
            global pages	
            pages = ceil(tasks/STATUS_LIMIT)	
            if PAGE_NO > pages and pages != 0:	
                globals()['COUNT'] -= STATUS_LIMIT	
                globals()['PAGE_NO'] -= 1	
        msg = f"<b> Dᴏᴡɴʟᴏᴀᴅɪɴɢ 📤: {num_active} || Uᴘʟᴏᴀᴅɪɴɢ 📤: {num_upload} || Sᴇᴇᴅɪɴɢ 🌧: {num_seeding}</b>\n\n"       	
        for index, download in enumerate(list(download_dict.values())[COUNT:], start=1):	
            reply_to = download.message.reply_to_message	
            msg += f"<b>• Fɪʟᴇɴᴀᴍᴇ:</b> <code>{escape(str(download.name()))}</code>"	
            msg += f"\n<b>• Sᴛᴀᴛᴜs​:</b> <b>{download.status()}</b>"	
            if download.status() not in [	
                MirrorStatus.STATUS_ARCHIVING,	
                MirrorStatus.STATUS_EXTRACTING,	
                MirrorStatus.STATUS_SPLITTING,	
                MirrorStatus.STATUS_SEEDING,	
            ]:	
                msg += f"\n{get_progress_bar_string(download)} {download.progress()}"	
                if download.status() == MirrorStatus.STATUS_CLONING:	
                    msg += f"\n<b>• CLᴏɴᴇᴅ:</b> {get_readable_file_size(download.processed_bytes())} of {download.size()}"	
                elif download.status() == MirrorStatus.STATUS_UPLOADING:	
                    msg += f"\n<b>• Uᴘʟᴏᴀᴅᴇᴅ:</b> {get_readable_file_size(download.processed_bytes())} of {download.size()}"	
                else:	
                    msg += f"\n<b>• Dᴏᴡɴʟᴏᴀᴅᴇᴅ:</b> {get_readable_file_size(download.processed_bytes())} of {download.size()}"	
                msg += f"\n<b>• Sᴘᴇᴇᴅ:</b> {download.speed()} | <b>Eᴛᴀ Tɪᴍᴇ:</b> {download.eta()}"	
                if reply_to:	
                    msg += f"\n• Aᴅᴅᴇᴅ Bʏ: <a href='tg://user?id={download.message.from_user.id}'>{download.message.from_user.first_name}</a> (<code>{download.message.from_user.id}</code>)"	
                else:	
                    msg += f"\n• Aᴅᴅᴇᴅ Bʏ: <a href='tg://user?id={download.message.from_user.id}'>{download.message.from_user.first_name}</a> (<code>{download.message.from_user.id}</code>)"		
                try:
                    msg += f"\n<i>Aria2📶</i> | • Seeders: {download.aria_download().num_seeders}" \
                           f" | • Peers: {download.aria_download().connections}"
                except:
                    pass
                try: 
                    msg += f"\n<i>qbit🦠</i> | • Seeders: {download.torrent_info().num_seeds}" \
                           f" | • Leechers: {download.torrent_info().num_leechs}"
                except:
                    pass	
                msg += f"\n• Tᴏ Cᴀɴᴄᴇʟ​: <code>/{BotCommands.CancelMirror} {download.gid()}</code>\n\n═════════════════════ "	
            elif download.status() == MirrorStatus.STATUS_SEEDING:	
                msg += f"\n<b>• Sɪᴢᴇ: </b>{download.size()}"	
                msg += f"\n<b>• Sᴘᴇᴇᴅ: </b>{get_readable_file_size(download.torrent_info().upspeed)}/s"	
                msg += f" | <b>• Uᴘʟᴏᴀᴅᴇᴅ: </b>{get_readable_file_size(download.torrent_info().uploaded)}"	
                msg += f"\n<b>• Rᴀᴛɪᴏ: </b>{round(download.torrent_info().ratio, 3)}"	
                msg += f" | <b>• Tɪᴍᴇ: </b>{get_readable_time(download.torrent_info().seeding_time)}"	
                msg += f"\n<code>/{BotCommands.CancelMirror} {download.gid()}</code>"	
            else:	
                msg += f"\n<b>• Sɪᴢᴇ: </b>{download.size()}"	
            msg += "\n\n"	
            if STATUS_LIMIT is not None and index == STATUS_LIMIT:	
                break	
        currentTime = get_readable_time(time() - botStartTime)
        for download in list(download_dict.values()):
            speedy = download.speed()
            if download.status() == MirrorStatus.STATUS_DOWNLOADING:
                if 'K' in speedy:
                    dlspeed_bytes += float(speedy.split('K')[0]) * 1024
                elif 'M' in speedy:
                    dlspeed_bytes += float(speedy.split('M')[0]) * 1048576
            if download.status() == MirrorStatus.STATUS_UPLOADING:
                if 'KB/s' in speedy:
                    uldl_bytes += float(speedy.split('K')[0]) * 1024
                elif 'MB/s' in speedy:
                    uldl_bytes += float(speedy.split('M')[0]) * 1048576
        dlspeed = get_readable_file_size(dlspeed_bytes)
        ulspeed = get_readable_file_size(uldl_bytes)
        msg += f"\n📖 Pages: {PAGE_NO}/{pages} | 📝 Tasks: {tasks}"
        msg += f"\nBOT UPTIME: <code>{currentTime}</code>"
        msg += f"\nDL: {dlspeed}/s🔻 | UL: {ulspeed}/s🔺"
        buttons = ButtonMaker()
        buttons.sbutton("🔄", str(ONE))
        buttons.sbutton("❌", str(TWO))
        buttons.sbutton("📈", str(THREE))
        sbutton = InlineKeyboardMarkup(buttons.build_menu(3))	
        if STATUS_LIMIT is not None and tasks > STATUS_LIMIT:	
            buttons = ButtonMaker()
            buttons.sbutton("⬅️", "status pre")
            buttons.sbutton("❌", str(TWO))
            buttons.sbutton("➡️", "status nex")
            buttons.sbutton("🔄", str(ONE))
            buttons.sbutton("📈", str(THREE))
            button = InlineKeyboardMarkup(buttons.build_menu(3))
            return msg, button
        return msg, sbutton
                
ONE, TWO, THREE = range(3)
                
def refresh(update, context):
    chat_id  = update.effective_chat.id
    query = update.callback_query
    user_id = update.callback_query.from_user.id
    query.edit_message_text(text="Refreshing...👻")
    sleep(1)
    query.answer(text="Refreshed", show_alert=False)
    
def close(update, context):  
    chat_id  = update.effective_chat.id
    user_id = update.callback_query.from_user.id
    bot = context.bot
    query = update.callback_query
    admins = bot.get_chat_member(chat_id, user_id).status in ['creator', 'administrator'] or user_id in [OWNER_ID] 
    if admins: 
        query.answer()  
        query.message.delete() 
    else:  
        query.answer(text="Nice Try, Get Lost🥱.\n\nOnly Admins can use this.", show_alert=True)
        
def stats(update, context):
    query = update.callback_query
    stats = bot_sys_stats()
    query.answer(text=stats, show_alert=True)

def bot_sys_stats():
    currentTime = get_readable_time(time() - botStartTime)
    cpu = cpu_percent(interval=0.5)
    memory = virtual_memory()
    mem = memory.percent
    total, used, free, disk= disk_usage('/')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    recv = get_readable_file_size(net_io_counters().bytes_recv)
    sent = get_readable_file_size(net_io_counters().bytes_sent)
    stats = f"""
BOT UPTIME: {currentTime}
CPU: {progress_bar(cpu)} {cpu}%
RAM: {progress_bar(mem)} {mem}%
DISK: {progress_bar(disk)} {disk}%
TOTAL: {total}
USED: {used} || FREE: {free}
SENT: {sent} || RECV: {recv}
#KristyCloud
"""
    return stats	

def turn(data):	
    try:	
        with download_dict_lock:	
            global COUNT, PAGE_NO	
            if data[1] == "nex":	
                if PAGE_NO == pages:	
                    COUNT = 0	
                    PAGE_NO = 1	
                else:	
                    COUNT += STATUS_LIMIT	
                    PAGE_NO += 1	
            elif data[1] == "pre":	
                if PAGE_NO == 1:	
                    COUNT = STATUS_LIMIT * (pages - 1)	
                    PAGE_NO = pages	
                else:	
                    COUNT -= STATUS_LIMIT	
                    PAGE_NO -= 1	
        return True	
    except:	
        return False	

def get_readable_time(seconds: int) -> str:	
    result = ''	
    (days, remainder) = divmod(seconds, 86400)	
    days = int(days)	
    if days != 0:	
        result += f'{days}d'	
    (hours, remainder) = divmod(remainder, 3600)	
    hours = int(hours)	
    if hours != 0:	
        result += f'{hours}h'	
    (minutes, seconds) = divmod(remainder, 60)	
    minutes = int(minutes)	
    if minutes != 0:	
        result += f'{minutes}m'	
    seconds = int(seconds)	
    result += f'{seconds}s'	
    return result	

def is_url(url: str):	
    url = re_findall(URL_REGEX, url)	
    return bool(url)	

def is_gdrive_link(url: str):	
    return "drive.google.com" in url	

def is_gdtot_link(url: str):	
    url = re_match(r'https?://.+\.gdtot\.\S+', url)	
    return bool(url)	

def is_mega_link(url: str):	
    return "mega.nz" in url or "mega.co.nz" in url	

def get_mega_link_type(url: str):	
    if "folder" in url:	
        return "folder"	
    elif "file" in url:	
        return "file"	
    elif "/#F!" in url:	
        return "folder"	
    return "file"	

def is_magnet(url: str):	
    magnet = re_findall(MAGNET_REGEX, url)	
    return bool(magnet)	

def new_thread(fn):	
    """To use as decorator to make a function call threaded.	
    Needs import	
    from threading import Thread"""	

    def wrapper(*args, **kwargs):	
        thread = Thread(target=fn, args=args, kwargs=kwargs)	
        thread.start()	
        return thread	

    return wrapper	

def get_content_type(link: str) -> str:	
    try:	
        res = rhead(link, allow_redirects=True, timeout=5, headers = {'user-agent': 'Wget/1.12'})	
        content_type = res.headers.get('content-type')	
    except:	
        try:	
            res = urlopen(link, timeout=5)	
            info = res.info()	
            content_type = info.get_content_type()	
        except:	
            content_type = None	
    return content_type	

dispatcher.add_handler(CallbackQueryHandler(refresh, pattern='^' + str(ONE) + '$'))
dispatcher.add_handler(CallbackQueryHandler(close, pattern='^' + str(TWO) + '$'))
dispatcher.add_handler(CallbackQueryHandler(stats, pattern='^' + str(THREE) + '$'))
