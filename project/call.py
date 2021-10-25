# # -*- codeing = utf-8 -*-
# # @Time : 2021/9/29 22:28
# # @Author : 黎满
# # @File : call.py
# # @Software : PyCharm
#
# import paramiko
# ip = "192.168.137.254"
# port = 22
# user = "root"
# password = "root"
# # 创建SSHClient 实例对象
# ssh = paramiko.SSHClient()
# # 调用方法，表示没有存储远程机器的公钥，允许访问
# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# # 连接远程机器，地址，端口，用户名密码
# # print(self.ip, self.sshpasswd, self.sshusename)
# # print(self.ip,self.sshname,self.sshpasswd)
# ssh.connect(ip, port, user, password, timeout=10)
# # 输入linux命令
# cmd = "python startupFile.py"
# # ls = "ls"
# ssh.exec_command(cmd)
# # 输出命令执行结果
# # result = stdout.read()
# print("成功执行命令")
# # 关闭连接
# ssh.close()