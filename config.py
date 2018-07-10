
import os

ENVIRON=os.environ

class SettingHolder(object):

    NEO_ASSETID = "0xc56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b"
    GAS_ASSETID = "0x602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"

    MYSQLDATABASE = {
        "host": "127.0.0.1",
        "user": ENVIRON.get("DATABASE_USERNAME"),
        "passwd": ENVIRON.get("DATABASE_PASSWORD"),
        "db": ENVIRON.get("DATABASE_DB"),
        "db_block_info": ENVIRON.get("DATABASE_DB_BLOCK_INFO"),
        "db_account_info": ENVIRON.get("DATABASE_DB_ACCOUNT_INFO"),
    }

    def setup_mainnet(self):
        self.CONTRACTHASH="0x08e8c4400f1af2c20c28e0018f29535eb85d15b6"
        self.NEOCLIURL = "http://127.0.0.1:10332"
        self.APPLICATIONLOGDIR = "/root/neo/neo-cli/ApplicationLogs_00746E41"
        self.PRIVTKEY=ENVIRON.get("PRIVTKEY")
        self.PASSWD_HASH="$2b$10$F7GVmj.eahbHMIUjOxooYuLBMqZaIGcJZ7KxufGfbxwGTErKCzNQm"
        self.REMOTE_ADDR=ENVIRON.get("REMOTE_ADDR")
        self.FUNDING_ADDRESS=ENVIRON.get("FUNDING_ADDRESS")
        self.WEBAPI=ENVIRON.get("WEB_API")
    def setup_testnet(self):
        self.CONTRACTHASH = "0x849d095d07950b9e56d0c895ec48ec5100cfdff1"
        self.NEOCLIURL = "http://127.0.0.1:20332"
        self.APPLICATIONLOGDIR="/root/neo-cli-274/ApplicationLogs_74746E41"
        self.PRIVTKEY=ENVIRON.get("PRIVTKEY")
        self.PASSWD_HASH=ENVIRON.get("PASSWORD_HASH")
        self.REMOTE_ADDR=ENVIRON.get("REMOTE_ADDR")
        self.FUNDING_ADDRESS=ENVIRON.get("FUNDING_ADDRESS")
        self.WEBAPI=ENVIRON.get("WEB_API")
        self.REDIS_IP="47.104.81.20"
        self.REDIS_PORT=9001
    def setup_privtnet(self):
        self.CONTRACTHASH = "0x0c34a8fd0109df360c7cf7ca454404901db77f5e"
        self.NEOCLIURL = "http://localhost:10332"
        self.REDIS_IP="localhost"
        self.REDIS_PORT=6379

setting=SettingHolder()

if ENVIRON.get("CURRENT_ENVIRON") == "testnet":
    setting.setup_testnet()
elif ENVIRON.get("CURRENT_ENVIRON") == "mainnet":
    setting.setup_mainnet()
else:
    setting.setup_privtnet()
