#日志文件目录和名称
import subprocess

filename = 'log/a.log'
#要执行的shell命令
command='tailf '+filename+'|grep "Traceback"'
popen=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
while True:
    #获取当前grep出来的日志文本行
    line=popen.stdout.readline()
    print(line)