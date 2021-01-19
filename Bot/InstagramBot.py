import requests
from selenium.common.exceptions import NoSuchElementException
from seleniumwire import webdriver as wire_webdriver
from webdriver_manager.driver import ChromeDriver
from webdriver_manager import logger as wdm_logger

from Bot import bot_config as config
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChOptions
from selenium.webdriver.firefox.options import Options as FiOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import random
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.common.keys import Keys
import os
import time
from datetime import datetime
from Bot.enums import BotErrors, PostTypes, Constants, Browser, Tabs
from RunSchedule import RunSchedule as schedule
from Bot.models import Post, User, InstaComment, PageInfo
import pickle
from DAL import repositories
import json


class InstagramBot:

    def follow_followers(self, target_user_name, max=20, follow_hour=20):
        user_names = []
        try:
            valid, error = self.get_and_validate_page(target_user_name)
            if not valid:
                return None, error

            a_tags = self.webdriver.find_elements_by_css_selector("ul li a")
            followers_link = [l for l in a_tags if ('followers' in l.text)][0]
            followers_link.click()
            time.sleep(10)

            follower_list_dialoge = self.webdriver.find_element_by_css_selector("div[role=\'dialog\'] ul")
            follower_list_dialoge.click()

            loop_counter = 0
            last_count = 0
            while len(user_names) < max and loop_counter < config.max_loop_count:
                self.webdriver.execute_script("arguments[0].scrollIntoView(true);", follower_list_dialoge)
                time.sleep(0.5)
                self.webdriver.execute_script("arguments[0].scrollIntoView(false);", follower_list_dialoge)
                time.sleep(2)

                followers_li = follower_list_dialoge.find_elements_by_css_selector("li")
                if len(followers_li) == last_count:
                    loop_counter += 1
                else:
                    loop_counter = 0
                last_count = len(followers_li)

                for li in followers_li:
                    user_link = li.find_element_by_css_selector("a").get_attribute("href")
                    user_name = user_link.strip('/').split('/')[-1]
                    button = li.find_element_by_css_selector("button")
                    if button.text.lower() == "follow":
                        button.click()
                        time.sleep(10)
                        dialogs = self.webdriver.find_elements_by_css_selector("div[role=\'dialog\']")
                        for d in dialogs:
                            if config.insta_block_text in d.text.lower():
                                return None, BotErrors.InstaBlock
                        if button.text.lower() == "requested" or "following":
                            user_names.append(user_name)
                            yield user_name, None
                            sleep_time = schedule.get_random_time_from_hourly_avreage(follow_hour)
                            time.sleep(sleep_time)

        except Exception as e:
            return None, BotErrors.Unknown

    def unfollow_following(self, unfollow_list, follower_list, unfollow_hour, unfollow_followers=False):
        try:
            valid, err = self.get_and_validate_page(self.username)
            if not valid:
                return None, err

            a_tags = self.webdriver.find_elements_by_css_selector("ul li a")
            following_link = [l for l in a_tags if ('following' in l.text)][0]
            span = following_link.find_element_by_css_selector('span')
            following_count = int(span.text.replace(',', ''))
            following_link.click()
            time.sleep(10)

            following_list_dialoge = self.webdriver.find_element_by_css_selector("div[role=\'dialog\'] ul")
            following_list_dialoge.click()

            followings_li = []
            loop_counter = 0
            last_count = 0
            while len(followings_li) < following_count and loop_counter < config.max_loop_count:
                self.webdriver.execute_script("arguments[0].scrollIntoView(true)", following_list_dialoge)
                time.sleep(0.5)
                self.webdriver.execute_script("arguments[0].scrollIntoView(false)", following_list_dialoge)
                time.sleep(1)

                followings_li = following_list_dialoge.find_elements_by_css_selector("li")
                if len(followings_li) == last_count:
                    loop_counter += 1
                else:
                    loop_counter = 0

                last_count = len(followings_li)

            for li in followings_li:
                user_link = li.find_element_by_css_selector("a").get_attribute("href")
                user_name = user_link.strip('/').split('/')[-1]

                if True or (user_name in unfollow_list and \
                            (not unfollow_followers or user_name not in follower_list)):
                    button = li.find_element_by_css_selector("button")
                    if button.text.lower() == 'following':
                        button.click()
                        time.sleep(10)
                        dialogs = self.webdriver.find_elements_by_css_selector("div[role=\'dialog\']")
                        for d in dialogs:
                            if len(d.find_elements_by_css_selector("ul")) == 0:
                                buttons = d.find_elements_by_css_selector("button")
                                for b in buttons:
                                    if 'unfollow' in b.text.lower():
                                        b.click()
                                        time.sleep(10)
                                        inner_dialogs = self.webdriver.find_elements_by_css_selector(
                                            "div[role=\'dialog\']")
                                        for id in inner_dialogs:
                                            if config.insta_block_text in id.text.lower():
                                                return None, BotErrors.InstaBlock
                                        if 'follow' in button.text.lower():
                                            sleep_time = schedule.get_random_time_from_hourly_avreage(unfollow_hour)
                                            yield user_name, sleep_time
                                            time.sleep(sleep_time)
                                            break

        except Exception as e:
            return None, BotErrors.Unknown

    def __init__(self, username, password, hidden=True, browser=Browser.Chrome, proxy=None):
        self.username = username
        self.password = password
        self.tabs = {}
        # options.add_argument("start-maximized")
        # options.add_argument("user-data-dir="+f'{config.chrome_user_data_dir}\\{self.username}')
        # options.add_argument('--remote-debugging-port=9222')
        # options.add_argument("--profile-directory="+f'{config.user_data_dir}/{self.username}')

        # chrome
        # chrome_driver_path = os.getcwd() + config.firefox_driver_path
        # self.webdriver = webdriver.Firefox(executable_path=chrome_driver_path, options=options

        # firefox
        driver_path = ''
        options = None
        if browser == Browser.Chrome:
            driver_path = os.getcwd() + config.chrome_driver_path
            options = ChOptions()

            # if proxy_plugin_file:
            #     options.add_extension(proxy_plugin_file)

            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
            options.add_argument("--log-level=3")
            options.headless = hidden
            wire_options = {}
            if proxy:
                wire_options = {
                    'proxy': {
                        'http': 'http://{}:{}@{}:{}'.format(proxy.Username, proxy.Password, proxy.Address, proxy.Port),
                        'https': 'https://{}:{}@{}:{}'.format(proxy.Username, proxy.Password, proxy.Address, proxy.Port),
                    }
                }

            # add proxy to chromDriverManager
            def get_latest_release_version_with_proxy(self):
                wdm_logger.log(f"Get LATEST driver version for {self.browser_version}")
                resp = ''
                try:
                    resp = requests.get(f"{self._latest_release_url}_{self.browser_version}", proxies=wire_options.get('proxy', None))
                except Exception as e:
                    print(e)
                if resp.status_code == 404:
                    raise ValueError("There is no such driver by url {}".format(resp.url))
                elif resp.status_code != 200:
                    raise ValueError(resp.json())
                return resp.text.rstrip()

            ChromeDriver.get_latest_release_version = get_latest_release_version_with_proxy
            self.webdriver = wire_webdriver.Chrome(executable_path=ChromeDriverManager(cache_valid_range=30).install(), options=options, seleniumwire_options=wire_options)
        elif browser == Browser.Firefox:
            driver_path = os.getcwd() + config.firefox_driver_path
            options = FiOptions()
            options.headless = hidden
            self.webdriver = webdriver.Firefox(executable_path=GeckoDriverManager(cache_valid_range=30).install(), options=options)

        self.webdriver.get('https://httpbin.org/ip')
        try:
            pass
        except Exception as e:
            pass

    def open(self, use_cookie=True):
        try:
            self.webdriver.get(config.instaBaseLink)
            time.sleep(5)
            self.check_accept_cookies()
            if use_cookie and self.cookie_exist(self.username):
                self.load_cookie()
                self.webdriver.get(config.instaBaseLink)
                time.sleep(5)
            is_login, _ = self.is_login()
            err = None
            while not is_login:
                is_login, err = self.login()
                if err:
                    if err == BotErrors.InstaTempLocked:
                        print(config.insta_temp_locked)
                        break
                    elif err == BotErrors.Pass_Incorrect:
                        print(config.insta_wrongpass_text)
                        break
                    elif err == BotErrors.User_Incorrect:
                        print(config.insta_wronguser_text)
                        break
                    elif err == BotErrors.InstaError:
                        print(config.insta_error_text)
                        break
                    elif err == BotErrors.Couldnt_Connet_Insta:
                        print(config.insta_couldnt_connect_text)
                        break
                    else:
                        print(config.insta_error_text)
                time.sleep(5)
            if not is_login:
                self.close()
            return is_login, err

        except Exception as e:
            return False, BotErrors.Unknown

    def login(self):
        try:
            #self.webdriver.get(config.instaBaseLink + config.instaLoginLink)
            valid, err = self.get_and_validate_page(config.instaLoginLink)
            is_login, _ = self.is_login()
            if is_login:
                self.save_cookie()
                return True, None

            if valid:
                self.check_accept_cookies()
                input_counts = 0
                loop_counter = 0
                form_inputs = []
                while input_counts == 0 and loop_counter < config.max_loop_count:
                    form_inputs = self.webdriver.find_elements_by_css_selector('form input')
                    input_counts = len(form_inputs)
                    loop_counter += 1
                    time.sleep(10)

                if loop_counter >= config.max_loop_count:
                    return False, BotErrors.Login_Failed

                username_input = form_inputs[0]
                pass_input = form_inputs[1]

                username_input.send_keys(self.username)
                pass_input.send_keys(self.password)
                pass_input.send_keys(Keys.RETURN)
                time.sleep(10)

                errors = self.webdriver.find_elements_by_id('slfErrorAlert')
                if len(errors):
                    if config.insta_wrongpass_text.lower() in errors[0].text.lower():
                        return False, BotErrors.Pass_Incorrect
                    elif config.insta_wronguser_text.lower() in errors[0].text.lower():
                        return False, BotErrors.User_Incorrect
                    elif config.insta_couldnt_connect_text.lower() in errors[0].text.lower():
                        return False, BotErrors.Couldnt_Connet_Insta
                    else:
                        return False, BotErrors.Internet_Problems
                is_login, _ = self.is_login()
                if is_login:
                    self.save_cookie()

                return is_login, err
            else:
                return valid, err
        except Exception as e:
            return False, BotErrors.Unknown

    def is_login(self):
        try:
            home_icon = self.webdriver.find_elements_by_css_selector('svg[aria-label="Home"')
            explore_icon = self.webdriver.find_elements_by_css_selector('svg[aria-label="Find People"')
            activity_icon = self.webdriver.find_elements_by_css_selector('svg[aria-label="Activity Feed"')

            if len(home_icon) > 0 and len(explore_icon) > 0 and len(activity_icon) > 0:
                return True, None
            else:
                return False, None

        except Exception as e:
            return False, BotErrors.Unknown

    def follow_followers2(self, target_user_name, max=20, follow_hour=20):
        user_names = []
        try:
            valid, err = self.get_and_validate_page(target_user_name)
            if not valid:
                yield None, err
                return

            for followers_li, error in self.get_dialog_list('followers'):

                if error is not None:
                    yield None, error
                    return
                for li in followers_li:
                    if len(user_names) == max:
                        return

                    user_link = li.find_element_by_css_selector("a").get_attribute("href")
                    fullname = li.find_element_by_css_selector('li div div:nth-of-type(2) div:nth-of-type(2)').text
                    imgurl = li.find_element_by_css_selector('img').get_attribute('src')
                    user = User(user_link,fullname,imgurl)
                    repository = repositories.WorkPageInstaUserRepository()
                    button = li.find_element_by_css_selector("button")
                    if button.text.lower() == "follow":
                        if not repository.already_followed(user.username, self.username):
                            button.click()
                            time.sleep(10)

                            err = self.check_if_blocked()
                            if err:
                                yield None, err
                                return

                            if button.text.lower() == "requested" or button.text.lower() == "following":
                                yield user, None

        except Exception as e:
            yield None, BotErrors.Unknown

    def unfollow_following2(self, unfollow_list, follower_list, ignore_followers=True):
        try:
            valid, err = self.get_and_validate_page(self.username)
            if not valid:
                yield None, err
                return

            followings_li = []
            for list, error in self.get_dialog_list('following', max=1200):
                if error is not None:
                    yield None, error
                    return
                followings_li = list

            for j in range(len(followings_li)-2, -1, -1):
                li = followings_li[j]
                user_link = li.find_element_by_css_selector("a").get_attribute("href")
                user_name = user_link.strip('/').split('/')[-1]

                if (user_name in unfollow_list and
                     (not ignore_followers or user_name not in follower_list)):
                    button = li.find_element_by_css_selector("button")
                    if button.text.lower() == 'following':
                        button.click()
                        time.sleep(2)
                        dialogs = self.webdriver.find_elements_by_css_selector("div[role=\'dialog\']")
                        for d in dialogs:
                            if len(d.find_elements_by_css_selector("ul")) == 0:
                                buttons = d.find_elements_by_css_selector("button")
                                for b in buttons:
                                    if 'unfollow' in b.text.lower():
                                        b.click()
                                        time.sleep(10)
                                        err = self.check_if_blocked()
                                        if err:
                                            yield None, err
                                            return

                                        if 'follow' in button.text.lower():
                                            yield user_name, None
                                        break

        except Exception as e:
            yield None, BotErrors.Unknown

    def get_followers(self):
        try:
            valid, err = self.get_and_validate_page(self.username)
            if not valid:
                return None, err

            followers_li = []
            for list in self.get_dialog_list('followers'):
                followers_li = list

            follower_list = []
            for li in followers_li:
                if len(li.find_elements_by_css_selector("a")) == 0:
                    continue
                user_link = li.find_element_by_css_selector("a").get_attribute("href")
                user_name = user_link.strip('/').split('/')[-1]
                follower_list.append(user_name)
            return follower_list

        except Exception as e:
            return None, BotErrors.Unknown

    def get_numbers(self, text):
        count = 0
        try:
            if 'm' in text.lower():
                count = int(float(text.replace('m', '').replace(',', '')) * 1000000)
            elif 'k' in text.lower():
                count = int(float(text.replace('k', '').replace(',', '')) * 1000)
            else:
                count = int(text.replace(',', ''))
        except Exception as e:
            pass
        return count

    def get_dialog_list(self, list_name, max=1000):
        try:
            a_tags = self.webdriver.find_elements_by_css_selector("ul li a")
            thelink = [l for l in a_tags if (list_name in l.text)][0]
            span = thelink.find_element_by_css_selector('span')
            count = 0
            if 'm' in span.text.lower():
                count = int(float(span.text.replace('m', '').replace(',', '')) * 1000000)
            elif 'k' in span.text.lower():
                count = int(float(span.text.replace('k', '').replace(',', '')) * 1000)
            else:
                count = int(span.text.replace(',', ''))
            thelink.click()
            time.sleep(10)

            list_dialog = self.webdriver.find_element_by_css_selector("div[role=\'dialog\'] ul")
            list_dialog.click()

            list_li = []
            loop_counter = 0
            last_count = 0
            while len(list_li) < count and len(list_li) < max and loop_counter < config.max_loop_count:
                self.go_up_down(list_dialog)

                list_li = list_dialog.find_elements_by_css_selector("li")
                if len(list_li) == last_count:
                    loop_counter += 1
                else:
                    loop_counter = 0
                last_count = len(list_li)
                yield list_li, None
        except NoSuchElementException:
            yield None, BotErrors.InstaNotLoadList
        except:
            yield None, BotErrors.Unknown

    def get_posts(self, username, post_count):
        posts = {}
        try:
            valid, err = self.get_and_validate_page(username)
            if not valid:
                return None, err

            articles = self.webdriver.find_elements_by_css_selector("article")
            if len(articles) != 1:
                return None, BotErrors.Unknown

            article = articles[0]

            while len(posts.keys()) < post_count:
                post_a_tags = article.find_elements_by_css_selector("a")
                for a_tag in post_a_tags:
                    action = ActionChains(self.webdriver)
                    action.move_to_element(a_tag).perform()
                    time.sleep(0.5)
                    url = a_tag.get_attribute("href")
                    key = url.split(config.instaBaseLink)[-1]
                    post = Post(a_tag, url)
                    spans = a_tag.find_elements_by_css_selector("span[aria-label]")
                    if len(spans) == 1:
                        type = spans[0].get_attribute("aria-label")
                        if type.lower() == "video" or type.lower() == "igtv":
                            post.set_type(PostTypes.Video)
                        elif type.lower() == "carousel":
                            post.set_type(PostTypes.MultiImage)

                    li_list = a_tag.find_elements_by_css_selector('ul li')
                    likes, comments, views = 0,0,0
                    for li in li_list:
                        spans = li.find_elements_by_css_selector('span')
                        count = 0
                        type = ''
                        for span in spans:
                            if 'heart' in span.get_attribute('class').lower():
                                type = 'like'
                            elif 'speech' in span.get_attribute('class').lower():
                                type = 'comment'
                            elif 'play' in span.get_attribute('class').lower():
                                type = 'view'
                            else:
                                count = self.get_numbers(span.text)

                        if type == 'comment':
                            comments = count
                        elif type == 'like':
                            likes = count
                        elif type == 'view':
                            views = count
                    post.set_stats(comments, likes, views)

                    posts[key] = post
                    if len(posts.keys()) >= post_count:
                        break


                self.go_up_down(article)

            return posts, None

        except Exception as e:
            return posts, BotErrors.Unknown

    def open_post(self, post):
        try:
            post.element.click()
            time.sleep(20)
            return True
        except Exception as e:
            return None

    def like_post(self, close_after=True):
        success = False
        try:
            like_buttons = self.webdriver.find_elements_by_css_selector('article section span '
                                                                        'button div svg[aria-label="Like"]')
            if len(like_buttons) == 1:
                like_button = like_buttons[0]
                like_button.click()
                time.sleep(5)

                err = self.check_if_blocked()
                if err:
                    return False, err

                unlike_buttons = self.webdriver.find_elements_by_css_selector('article section span '
                                                                              'button div svg[aria-label="Unlike"]')
                if len(unlike_buttons) == 1:
                    success = True

            time.sleep(5)
            if close_after:
                self.close_post()
            return success, None

        except Exception as e:
            return False, BotErrors.Unknown

    def follow_post_likers(self, max=2):
        follow_count = 0
        followed_usernames = []
        try:
            spans = self.webdriver.find_elements_by_css_selector('div>button>span')
            like_button = None
            for spn in spans:
                button = spn.find_element_by_xpath('..')
                div = button.find_element_by_xpath('..')
                if 'like' in div.text.lower():
                    like_button = button

            if like_button:
                like_button.click()
                time.sleep(5)

                divs = self.webdriver.find_elements_by_css_selector("div[aria-labelledby]")
                for div in divs:
                    a_tags = div.find_elements_by_css_selector('a')
                    buttons = div.find_elements_by_css_selector('button')
                    fullname = div.find_elements_by_css_selector('div div div:nth-of-type(2) div:nth-of-type(2) div:nth-of-type(2)')
                    imgurl = div.find_element_by_css_selector('img').get_attribute('src')

                    if len(a_tags) not in (1, 2) or len(buttons) != 1:
                        continue

                    button = buttons[0]
                    if button.text.lower() == 'follow':
                        a = a_tags[0]
                        user_link = a.get_attribute("href")
                        user_name = user_link.strip('/').split('/')[-1]
                        if len(fullname) == 1 and type(fullname) != str:
                            fullname = fullname[0].text
                        else:
                            fullname = ''
                        user = User(user_link, fullname, imgurl)
                        button.click()
                        time.sleep(10)
                        err = self.check_if_blocked()
                        if err:
                            yield False, err
                            return

                        if button.text.lower() == "requested" or button.text.lower() == "following":
                            followed_usernames.append(user_name)
                            follow_count += 1
                            yield user, None

                    if follow_count >= max:
                        close = div.find_element_by_xpath('..//..//..//..').find_element_by_css_selector(
                            'svg[aria-label="Close"]')
                        close.click()
                        break

            self.close_post()
            return

        except Exception as e:
            yield None, BotErrors.Unknown

    def comment_post(self, comment, close_after=True):
        success = False
        err = None
        try:
            forms = self.webdriver.find_elements_by_css_selector('section div form[method="POST"]')
            if len(forms) == 1:
                form = forms[0]
                form.click()
                textarea = form.find_element_by_css_selector('textarea')

                textarea.clear()
                # textarea.send_keys(comment)

                self.webdriver.execute_script(Constants.js_add_text_to_input, textarea, comment)
                time.sleep(0.5)
                textarea.send_keys(Keys.SPACE)
                time.sleep(0.5)

                button = form.find_element_by_css_selector('button')
                button.click()
                success = True
                err = None
                for i in range(20):
                    time.sleep(0.2)
                    p_tags = self.webdriver.find_elements_by_css_selector('body div div div div p')
                    for p in p_tags:
                        if config.insta_comment_blocked in p.text.lower():
                            success = False
                            err = BotErrors.InstaCommentBlocked
                            break
                    if not success:
                        break

            if close_after:
                self.close_post()
            return success, err

        except Exception as e:
            return False, BotErrors.Unknown

    def get_commenters_like_post_comments(self, old_comments, max_comment=1000, like_chance=0.7, max_likes=0.2, max_like_each_time=5):
        user_comments = []
        try:
            like_count = 0
            like_count_each_time = 0

            articles = self.webdriver.find_elements_by_css_selector('article')
            for article in articles:
                comment_li = article.find_elements_by_css_selector('ul li')
                if len(comment_li) == 0:
                    continue

                loop_count=0
                last_count = len(comment_li)
                while len(comment_li) - 1 < max_comment and loop_count < config.max_loop_count:
                    more_buttons = article.find_elements_by_css_selector('button span[aria-label="Load more comments"]')
                    if len(more_buttons) > 0:
                        more_button = more_buttons[0]
                        self.webdriver.execute_script("arguments[0].scrollIntoView(false);", more_button)
                        more_button.click()
                        time.sleep(5)
                        comment_li = article.find_elements_by_css_selector('ul li')
                        if len(comment_li) == last_count:
                            loop_count += 1
                        last_count = len(comment_li)
                    else:
                        loop_count += 1

                max_like_count = int(max_likes * len(comment_li))
                for li in comment_li:
                    if like_count < max_like_count:
                        verified = li.find_elements_by_css_selector('span[title="Verified"]')
                        if len(verified) > 0:
                            continue
                        url = ''
                        imgurl = ''
                        insta_comment_id = ''
                        insta_post_id = ''
                        comment_url = ''
                        a_tags = li.find_elements_by_css_selector('a')
                        for a in a_tags:
                            href = a.get_attribute('href')
                            if '/p/' in href and '/c/' in href:
                                comment_url=href
                                ids = href.split('/p/')[-1].split('/c/')
                                insta_comment_id = ids[-1].strip('/')
                                insta_post_id = ids[0].strip('/')

                            imgs = a.find_elements_by_css_selector('img')
                            if len(imgs) > 0:
                                url = a.get_attribute('href')
                                img = imgs[0]
                                imgurl = img.get_attribute('src')

                        if url == '' or insta_comment_id in old_comments:
                            continue

                        user = User(url, imageurl=imgurl)

                        comment_text = ''
                        spans = li.find_elements_by_css_selector('h3 + span')
                        for span in spans:
                            if span.text != '':
                                comment_text = span.text

                        liked = False
                        like_svgs = li.find_elements_by_css_selector('svg[aria-label="Like"]')
                        if len(like_svgs) == 1 and random.random() < like_chance:
                            like = like_svgs[0]
                            like.click()
                            time.sleep(5)
                            err = self.check_if_blocked()
                            if err:
                                yield user_comments, err
                                like_chance = 0
                            else:
                                liked = True
                                like_count += 1
                                like_count_each_time += 1

                        comment = InstaComment(insta_comment_id, comment_text, insta_post_id, user.username, comment_url)
                        user_comments.append((user, comment, liked))
                        if like_count_each_time >= max_like_each_time:
                            like_count_each_time = 0
                            yield user_comments, None
                            user_comments = []

            self.close_post()
            yield user_comments, None
            return

        except Exception as e:
            yield user_comments, BotErrors.Unknown
            return
        finally:
            self.close_post()

    def get_followers_profile(self):
        users_list = []
        try:
            valid, err = self.get_and_validate_page(config.instaProfileFollowersLink)
            if not valid:
                return None, err

            article = self.webdriver.find_element_by_css_selector("article")
            if article:
                button = article.find_element_by_css_selector('button')
                divs = article.find_elements_by_css_selector('div')
                print('followers:')
                while len(divs) < 200 and button:
                    button.click()
                    wait = random.randint(2,10)
                    time.sleep(wait)
                    button = article.find_element_by_css_selector('button')
                    divs = article.find_elements_by_css_selector('div')
                    print(len(divs), end='... ')

                users_list = [item.text for item in divs]
                return users_list, None
            else:
                return users_list, BotErrors.Unknown

        except Exception as e:
            return users_list, BotErrors.Unknown

    def close_post(self):
        try:
            close_buttons = self.webdriver.find_elements_by_css_selector('svg[aria-label="Close"]')
            if len(close_buttons) == 1:
                close_buttons[0].click()
        except:
            pass

    def check_if_blocked(self):
        dialogs = self.webdriver.find_elements_by_css_selector("div[role=\'dialog\']")
        error = None
        for d in dialogs:

            if config.insta_block_text in d.text.lower():
                error = BotErrors.InstaBlock

            if config.insta_try_again_text in d.text.lower():
                error = BotErrors.InstaTry

            if error:
                buttons = d.find_elements_by_css_selector('button')
                for button in buttons:
                    if config.insta_block_report_btn in button.text.lower() or config.insta_block_tellus_btn in button.text.lower():
                        button.click()
                        time.sleep(2)
                        break
        return error

    def get_and_validate_page(self, username):
        self.webdriver.get(config.instaBaseLink + username)
        time.sleep(5)
        self.check_accept_cookies()
        if config.insta_notavailable_text in self.webdriver.page_source.lower():
            return False, BotErrors.Not_Available
        elif config.insta_error_text in self.webdriver.page_source.lower():
            return False, BotErrors.InstaError
        elif config.insta_temp_locked in self.webdriver.page_source.lower():
            return False, BotErrors.InstaTempLocked
        else:
            return True, None

    def check_accept_cookies(self):
        dialogs = self.webdriver.find_elements_by_css_selector("div[role=\'dialog\']")
        done = False
        for d in dialogs:
            if config.insta_accept_cookies in d.text.lower():
                buttons = d.find_elements_by_css_selector('button')
                for b in buttons:
                    if 'accept' in b.text.lower():
                        b.click()
                        time.sleep(2)
                        done = True
                        break
            if done:
                break

    def go_up_down(self, element, up_delay=0.5, down_delay=2):
        self.webdriver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(up_delay)
        self.webdriver.execute_script("arguments[0].scrollIntoView(false);", element)
        time.sleep(down_delay)

    def take_screen_shot(self, name):
        try:
            self.webdriver.get_screenshot_as_file(name)
        except Exception as e:
            return False, BotErrors.Unknown

    def save_cookie(self):
        path = self.get_cookie_directory(self.username)
        with open(path, 'wb') as filehandler:
            pickle.dump(self.webdriver.get_cookies(), filehandler)

    def load_cookie(self):
        try:
            path = self.get_cookie_directory(self.username)
            with open(path, 'rb') as cookiesfile:
                cookies = pickle.load(cookiesfile)
                for cookie in cookies:
                    new_cookie = {}
                    new_cookie['name'] = cookie['name']
                    new_cookie['value'] = cookie['value']
                    self.webdriver.add_cookie(new_cookie)
        except Exception as e:
            pass

    @staticmethod
    def get_cookie_directory(username):
        today = datetime.today().strftime('%Y-%m-%d')
        temp_path = os.environ['localappdata']
        cookies_directory = f'{temp_path}\\{config.cookies_directory}\\{today}\\'
        path = f'{cookies_directory}{username}'
        if not os.path.exists(cookies_directory):
            os.makedirs(cookies_directory)
        return path

    @staticmethod
    def cookie_exist(username):
        cookie = InstagramBot.get_cookie_directory(username)
        return os.path.isfile(cookie)

    def close(self):
        try:
            is_login, _ = self.is_login()
            if is_login:
                self.save_cookie()
            self.webdriver.quit()
            self.webdriver.close()
        except Exception as e:
            pass

    def create_new_tab(self):
        self.webdriver.execute_script("window.open('','_blank');")
        self.webdriver.switch_to.window(self.webdriver.window_handles[-1])
        return self.webdriver.current_window_handle

    def create_tabs(self):
        tab_name = self.webdriver.current_window_handle

        for tab in Tabs:
            if tab != Tabs.GetFollowers:
                tab_name = self.create_new_tab()
            self.tabs[tab] = tab_name

    def switch_to_tab(self, tab):
        if self.tabs[tab]:
            self.webdriver.switch_to.window(self.tabs[tab])

    def is_tab_open(self, tab):
        open_tabs = self.webdriver.window_handles
        return self.tabs[tab] in open_tabs

    def open_tab(self, tab):
        tab_name = self.create_new_tab()
        self.tabs[tab] = tab_name

    def close_tab(self, tab):
        open_tabs = [name for name, value in self.tabs.items() if value is not None]
        if len(open_tabs) > 1 and self.is_tab_open(tab):
            self.switch_to_tab(tab)
            self.tabs[tab] = None
            self.webdriver.close()
            open_tab = [name for name, value in self.tabs.items() if value is not None][0]
            self.switch_to_tab(open_tab)

    def get_page_info(self, username):

        self.get_and_validate_page(username+ "/?__a=1")
        json_page = json.loads(self.webdriver.find_element_by_css_selector('body').text)
        try:
            user = json_page['graphql']['user']
            followers = user['edge_followed_by']['count']
            following = user['edge_follow']['count']
            full_name = user['full_name']
            post_count = user['edge_owner_to_timeline_media']['count']
            image = user['profile_pic_url_hd']
            image_hd = user['profile_pic_url']
            id = user['id']
            page_info = PageInfo(username, followers, following, full_name, post_count, image, image_hd, id)
            return page_info, None
        except Exception as e:
            return None, e




if __name__ == '__main__':

    bot = InstagramBot('nazissanad1', '773866qQ123!', False)


    bot.webdriver.switch_to.window(bot.webdriver.window_handles[2])
    bot.webdriver.close()
    bot.webdriver.switch_to.window(bot.webdriver.window_handles[0])
    bot.webdriver.switch_to.window(bot.webdriver.window_handles[1])
    bot.webdriver.close()
    bot.webdriver.switch_to.window(bot.webdriver.window_handles[3])

    m = bot.webdriver.window_handles

    bot.open()

    for user, error in bot.unfollow_following2([], [], 40, False):
        if user is None:
            print(error.name)
        else:
            print(user, 'is unfollowed! ', error / 60)

    posts, _ = bot.get_posts('laliga', 3)

    z = 0
    for a, b in posts.items():
        if z > 4:
            b.element.click()
            time.sleep(5)
            for user, comment, liked in bot.get_commenters_like_post_comments(50):
                print(user.username, 'comments: ', comment, 'on post:', b.url, 'and liked:', liked)
        z += 1

    bot.close()

    bot.take_screen_shot('test')
    for key, post in posts.items():
        post.element.click()
        time.sleep(5)
        bot.comment_post('')

    for a, b in posts.items():
        if b.type != PostTypes.Video:
            b.element.click()
            time.sleep(5)
            for x, y in bot.follow_post_likers():
                print(x)

    list = bot.get_followers()

    for user, error in bot.follow_followers2('perspolis', 3, 60):
        if user is None:
            print(error.name)
        else:
            print(user, 'is followed')

    for user, error in bot.unfollow_following([], [], 60, False):
        print(user, 'is unfollowed! ', error / 60)
    for user, error in bot.follow_followers('perspolis', 20, 20):
        print(user, 'is followed')
