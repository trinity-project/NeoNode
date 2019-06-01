import time
import requests
import os

from config import setting
from project_log.my_log import setup_logger



logger = setup_logger()

ENVIRON=os.environ
NO_REPLY_EMAIL_PAWD = ENVIRON.get("EMAIL_PASSWORD")

def execute_shell_command(command):
    import os
    os.system(command)


def request_block_height_from_neoscan(url):
    res = requests.get(url)
    if res.status_code == 200:
        return res.json().get("height")
    return None

def request_block_height_from_local(url):
    data = {
      "jsonrpc": "2.0",
      "method": "getblockcount",
      "params": [],
      "id": 1
}
    res = requests.post(url,json=data)
    if res.status_code == 200:
        return res.json().get("result")
    return None

def send_email(toAddr, local_block_number, infura_block_number):
    from email.header import Header
    from email.mime.text import MIMEText
    import smtplib

    msg = MIMEText(
        '''' 
        <!DOCTYPE html>
        <html>
        <head>
        </head>
        <body>
        <div id='preview-contents' class='note-content'>

        <h3 >title: restart neo node </h3>

        <p>local block number: {},neoscan block number:{}</p>

        </div>
        </body>
        </html>'''.format(local_block_number, infura_block_number), 'html', 'utf-8')

    msg['From'] = "no-reply@trinity.tech"
    msg['To'] = toAddr
    msg['Subject'] = Header('notification from WATCH NEO NODE.....')

    server = smtplib.SMTP_SSL("smtp.mxhichina.com", 465)  # SMTP协议默认端口是25
    server.login("no-reply@trinity.tech",NO_REPLY_EMAIL_PAWD )
    server.sendmail("no-reply@trinity.tech", [toAddr], msg.as_string())
    server.quit()


def compare_block_number():
    while True:
        try:
            neoscan_block_number = request_block_height_from_neoscan(setting.NEO_SCAN_API+"/get_height")
            local_block_number = request_block_height_from_local(setting.NEOCLIURL)
            logger.info("local_block_number:{},neoscan_block_number:{}".format(local_block_number, neoscan_block_number))
            if neoscan_block_number - local_block_number >= 20:
                execute_shell_command("supervisorctl restart dotnet")
                logger.warning("restart neo-cli")
                send_email("m17379352738@163.com", local_block_number, neoscan_block_number)
                time.sleep(10* 60)
        except:
            pass

        finally:
            time.sleep(120)


if __name__ == "__main__":
    compare_block_number()