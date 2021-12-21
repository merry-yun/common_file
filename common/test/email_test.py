# -*- coding: utf-8 -*-

from common import emailmodule


if __name__ == '__main__':
    smtp_server = 'smtp.qq.com'
    smtp_port = 25
    username = 'yatsenspider@qq.com'
    password = 'twhdlgbxthpedaha'
    smtp_service = emailmodule.SendEMailModule(smtp_server, smtp_port, username, password)

    email_msg = emailmodule.EMailMould()
    headers_dict = {
        'From': 'yatsenspider',
        'To': 'msl',
        'Subject': '注意查收附件',
    }
    for ehhkey in headers_dict.keys():
        email_msg.add_header(ehhkey, headers_dict[ehhkey])
    email_msg.add_text('如有问题请咨询相关人员')
    fpath = 'E:/Python_re/common/test/text.txt'
    email_msg.add_file(fpath, '附件1.txt')

    smtp_service.send_email('yatsenspider@qq.com', '1048893538@qq.com', email_msg())
    # email_msg.add_text('如有问题请咨询相关人员')
    # email_msg.add_file(fpath, '附件2.txt')
    # smtp_service.send_email('yatsenspider@qq.com', '1048893538@qq.com', email_msg())

    smtp_service.close()
