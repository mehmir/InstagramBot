import os
import zipfile


class ProxyManager:

    def __init__(self, host, port, user, password):
        self.proxy_host = host # '45.236.124.159'  # rotating proxy or host
        self.proxy_port = port # 999  # port
        self.proxy_user = user # 'hdkfpemm-dest'  # username
        self.proxy_pass = password # 'lrobwj3nkfi9'

    @staticmethod
    def get_manifest():
        manifest_json = """
                    {
                        "version": "1.0.0",
                        "manifest_version": 2,
                        "name": "Chrome Proxy",
                        "permissions": [
                            "proxy",
                            "tabs",
                            "unlimitedStorage",
                            "storage",
                            "<all_urls>",
                            "webRequest",
                            "webRequestBlocking"
                        ],
                        "background": {
                            "scripts": ["background.js"]
                        },
                        "minimum_chrome_version":"22.0.0"
                    }
                    """
        return manifest_json

    def get_background_js(self):
        background_js = """
                    var config = {
                            mode: "fixed_servers",
                            rules: {
                            singleProxy: {
                                scheme: "http",
                                host: "%s",
                                port: parseInt(%s)
                            },
                            bypassList: ["localhost"]
                            }
                        };

                    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

                    function callbackFn(details) {
                        return {
                            authCredentials: {
                                username: "%s",
                                password: "%s"
                            }
                        };
                    }

                    chrome.webRequest.onAuthRequired.addListener(
                                callbackFn,
                                {urls: ["<all_urls>"]},
                                ['blocking']
                    );
                    """ % (self.proxy_host, self.proxy_port, self.proxy_user, self.proxy_pass)
        return background_js

    def get_plugin_file(self):
        if not os.path.exists('proxies'):
            os.makedirs('proxies')
        pluginfile = 'proxies/proxy_auth_plugin_{}.zip'.format(self.proxy_host.strip().replace('.', '_'))
        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", self.get_manifest())
            zp.writestr("background.js", self.get_background_js())
        return pluginfile