import collections

from Bot import InstagramBot, BotErrors, config
from Bot.enums import WorkPageStatus
from DAL import repositories
import EncryptionTools


class BotService:

    @staticmethod
    def check_update_login(username):
        try:
            repository = repositories.WorkPageRepository()
            workpage, error = repository.get_workpage_by_username(username)

            if workpage:
                username = workpage.Username
                aes = EncryptionTools.AESCipher()
                password = "{:0>6}".format(aes.decrypt(workpage.Password))

                proxy = BotService.get_proxy(workpage)
                bot = InstagramBot(username, password, False, proxy=proxy)

                workpage_status = None
                is_login, err = bot.open(use_cookie=False)
                if err == BotErrors.InstaTempLocked:
                    print('Error:', config.insta_temp_locked)
                    workpage_status = WorkPageStatus.TempLocked
                elif err == BotErrors.Pass_Incorrect:
                    print('Error:', config.insta_wrongpass_text)
                    workpage_status = WorkPageStatus.WrongPassword
                elif err == BotErrors.User_Incorrect:
                    print('Error:', config.insta_wronguser_text)
                    workpage_status = WorkPageStatus.WrongUsername
                elif err == BotErrors.InstaError:
                    print('Error:', config.insta_error_text)
                    workpage_status = WorkPageStatus.Unknown
                elif err:
                    print('Error: some errors occurred:', err)
                    workpage_status = WorkPageStatus.Unknown

                bot.close()
                if is_login:
                    workpage_status = WorkPageStatus.Verified

                repository = repositories.WorkPageRepository()
                repository.update_status(username, workpage_status)
        except Exception:
            print(Exception)

    @staticmethod
    def update_page_info(page_username):
        repository = repositories.WorkPageRepository()
        workpages, error = repository.get_admin_workpages()

        bot = None
        for wp in workpages:
            try:
                username = wp.Username
                aes = EncryptionTools.AESCipher()
                password = "{:0>6}".format(aes.decrypt(wp.Password))
                proxy = BotService.get_proxy(wp)

                hide_browser = InstagramBot.cookie_exist(username)
                bot = InstagramBot(username, password, hide_browser, proxy=proxy)
                is_open, _ = bot.open()
                if is_open:
                    page_info, err = bot.get_page_info(page_username)
                    if page_info:
                        tp_repository = repositories.TargetPageRepository()
                        tp_repository.update_target_page_info(page_info)
                        break
                    else:
                        print(err)
            except Exception as e:
                print('Error:', e)
            finally:
                if bot:
                    bot.close()
                    del bot

    @staticmethod
    def get_proxy(workpage):
        repository = repositories.ProxyRepository()
        proxy, _ = repository.get(PROXY_ID=workpage.ProxyId)
        Proxy = collections.namedtuple('Proxy', 'Address Port Username Password')
        p = Proxy(proxy.Address, proxy.Port, proxy.Username, proxy.Password)
        return p