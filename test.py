from neocore.KeyPair import KeyPair
import binascii
# priv= binascii.unhexlify("38039B0629183DCE618EF1ED762C7AD0F2124E9EB7DE63A5F1CC4DCB47419A01")
# print(len(priv))
priv = KeyPair.PrivateKeyFromWIF("KwmEmHW1aa4ShM5XoaTTjhgMygGLLNAda7EwusiCoyqTpLKLd8fJ")
Key = KeyPair(priv)
print(Key.PrivateKey.hex())