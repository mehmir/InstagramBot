import base64
import hashlib
from Crypto.Cipher import AES
import pbkdf2


class AESCipher(object):
    key = 'TOPCompany Encrypted Strong password'

    def __init__(self):
        self.bs = 128#AES.block_size
        self.key = hashlib.sha256(AESCipher.key.encode()).digest()
        self.salt = bytes([1, 2, 3, 4, 5, 6, 7, 8])

#    def encrypt(self, raw):
#        raw = self._pad(raw)
#
#        derived_key = pbkdf2.PBKDF2(self.key, self.salt, 1000)
#        key = derived_key.read(32)
#        iv = derived_key.read(16)

#        cipher = AES.new(self.key, AES.MODE_CBC, iv)
#        return base64.b64encode(cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)

        derived_key = pbkdf2.PBKDF2(self.key, self.salt, 1000)
        key = derived_key.read(32)
        iv = derived_key.read(16)

        cipher = AES.new(key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc)).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


#aes = AESCipher()
#passw = aes.decrypt('hKBgjSSyd8Q8cYxUzwts7A==')
#aes = AESCipher('TOPCompany Encrypted Strong password')
#passw = aes.encrypt('773866qQ123')
#c = aes.decrypt(passw)
#a = 1