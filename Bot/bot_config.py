from Bot.enums import Browser

instaBaseLink = "https://www.instagram.com/"
instaLoginLink = "accounts/login/"
instaProfileFollowersLink = "accounts/access_tool/accounts_following_you"
#instaProfileFollowersLink = "accounts/access_tool/accounts_you_follow"

insta_notavailable_text = "sorry, this page isn't available."
insta_error_text = "please wait a few minutes before you try again."
insta_block_text = "blocked"
insta_wrongpass_text = 'your password was incorrect'
insta_wronguser_text = 'The username you entered doesn\'t belong to an account'
insta_try_again_text = 'try again later'
insta_comment_blocked = "couldn't post comment"
insta_block_report_btn = 'report a problem'
insta_block_tellus_btn = 'tell us'
insta_accept_cookies = 'accept cookies'
insta_temp_locked = 'your account has been temporarily locked'
insta_couldnt_connect_text = "We couldn\'t connect to Instagram. Make sure you\'re connected to the internet and try again."

browser = Browser.Chrome
chrome_driver_path = '\\drivers\\chromedriver.exe'
firefox_driver_path = '\\drivers\\geckodriver'
chrome_user_data_dir = '\\users browsers\\Chrome'
firefox_user_data_dir = 'c:\\users browsers\\Firefox'
cookies_directory = 'InstagramBot\\cookies'
max_loop_count = 20
max_post_comments = 1000
like_comments_chance = 0.3
wait_for_block = 1
wait_for_already_block = 6


# actions limits
