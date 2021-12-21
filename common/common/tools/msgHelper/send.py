#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2020/3/23 18:39
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2020/3/23 18:39
 * @Desc:
 修改
 * @version: 0.0.1
 * @Company:
 * @Author: stephen
 * @Last Modified by:   stephen
 * @Desc: 添加封装成类，根据返回的msg信息，自动化分类给响应的错误负责人
'''
import requests
import time


class MsgReport(object):

    def __init__(self, msg=None):
        self.msg = msg

    def classify_report(self):
        """
        根据返回的msg信息，自动分类给响应的错误负责人
        持续更新
        """
        print(f'get: {self.msg}')
        if 'cookies id' in self.msg and 'username:' in self.msg:
            touser = '张搌明,曹炜文'
            # touser = '曹炜文'
            result = self.send_text(msg=self.msg, touser=touser)
        else:
            result = self.send_text(msg='无法匹配到msg信息: ' + self.msg,
                                    touser='曹炜文')
        pass
    def classify_report_dict(self):
        """
        input dict{classify,message}
        :return:
        """
        if self.msg['classify'] == 'denglu':
            touser = '张搌明,曹炜文'
        elif self.msg['classify'] == 'ali':
            touser = '曹炜文'
        result = self.send_text(msg=self.msg['message'],touser=touser)

    def send_text(self, msg, timestamp=time.time(), touser=None):
        """
        发送信息给企业微信的人
        :param msg:  反馈信息内容
        :param timestamp:  时间戳，默认当前时间
        :param touser: 反馈人
        :return:  True / False
        """
        print("send msg: ", msg)
        print("toUser: ", touser)
        data = {"username": "曹炜文",
                "msg": msg,
                "timestamp": int(timestamp),
                "toUser": touser}
        result = requests.post(url="http://120.78.225.199:8000/newsendmsg", data=data)

        # result =requests.post(url="http://120.78.225.199:8000/remind", data=data)

        # data = {
        #     "username": "曹炜文",
        #     "sendname": toUser,
        #     "type": "message",
        #     "msg": "test曹炜文",
        #     "timestamp": timestamp,
        #     # "content": msg
        # }
        # result = requests.post("http://120.78.225.199:8000/remind", data=data).content.decode("utf-8", "ignore")
        print(result)
        if result.status_code is 200:
            return True
        else:
            return False

    def send_excel(self, out_path, toUser):
        files = {
            "file":open(out_path, "rb")
        }
        data = {
            "username":"曹炜文",
            "type":"file",
            "sendname":toUser
        }
        result = requests.post("http://120.78.225.199:8000/sendmsg", files=files, data=data)
        print(result.text)

    def chatbot_text(self, webhook=None, touser=[], content=None):
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            "msgtype": "text",
            "text": {
                "content": content,
                "mentioned_list": touser
                }
            }
        result = requests.post(webhook, json=data, headers=headers)
        return result

    def chatbot_makedown(self, webhook=None, touser=["@all"], makedown_content=None):
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": makedown_content,
                "mentioned_mobile_list": touser
            }
        }
        result = requests.post(
            webhook, json=data,
            headers=headers)
        return result


if "__main__" == __name__:
    # 测试
    msg = 'test'
    # report = MsgReport(msg=msg)
    # report.classify_report()
    url = r'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=252dc5e8-1485-43a8-9d25-b892e97bf104'
    report = MsgReport()
    print(report.chatbot_makedown(webhook=url, touser="zhangzhanming", makedown_content=msg))



