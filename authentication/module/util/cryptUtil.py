import base64
import hashlib

from Crypto import Random
from Crypto.Cipher import AES


class AESCipher(object):
    """
    A classical AES Cipher. Can use any size of data and any size of password thanks to padding.
    Also ensure the coherence and the type of the data with a unicode to byte converter.
    """
    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(AESCipher.str_to_bytes(key)).digest()

    @staticmethod
    def str_to_bytes(data):
        u_type = type(b''.decode('utf8'))
        if isinstance(data, u_type):
            return data.encode('utf8')
        return data

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * AESCipher.str_to_bytes(chr(self.bs - len(s) % self.bs))

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

    def encrypt(self, raw):
        raw = self._pad(AESCipher.str_to_bytes(raw))
        iv = Random.new().read(AES.block_size)
        aes_cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + aes_cipher.encrypt(raw)).decode('utf-8')

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        aes_cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(aes_cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

if __name__ == "__main__":

    key = 'supersecretkey'
    decrypted_password = 'pass'
    encrypted_password = 'o51WhrOqtptLoIqILOOlVSSZ9jAnyTLeaFfn8Eg/XRWGeiJN4RBVD9OpFpJ71bCo'

    cipher = AESCipher(key=key)
    
    cipher_decrypted_password = cipher.decrypt(encrypted_password)
    print(cipher_decrypted_password)

    print(decrypted_password == cipher_decrypted_password)
