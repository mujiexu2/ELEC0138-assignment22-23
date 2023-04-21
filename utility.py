'''
This file is used to generate images.
'''
import random
import string
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
from smtplib import SMTP_SSL

from email.header import Header
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ImageCode:
    def rand_color(self):
        """Generate a random color (any number between 0-255 can be specified) for drawing strings"""
        red = random.randint(32, 200)
        green = random.randint(22, 255)
        blue = random.randint(0, 200)
        return red, green, blue

    def gen_text(self):
        """Generate a 4-character random string."""
        # "sample" is used to randomly select N number of characters from a large list or string to construct a sub-list
        list = random.sample(string.ascii_letters, 4)
        return ''.join(list)

    def draw_verify_code(self):
        """Drawing the CAPTCHA image."""
        code = self.gen_text()
        width, height = 120, 50  # Set the image size, which can be adjusted according to actual needs
        im = Image.new('RGB', (width, height), 'white')  # Create an image object and set the background color to white
        font = ImageFont.truetype(font='arial.ttf', size=40)  # Choose what font and font size to use
        draw = ImageDraw.Draw(im)  # Create a new ImageDraw object

        # Render string
        for i in range(4):
            draw.text((5 + random.randint(-3, 3) + 23 * i, 5 + random.randint(-3, 3)), text=code[i],
                      fill=self.rand_color(), font=font)
            self.draw_lines(draw, 4, width, height)  # Drawing interference lines
        # im.show()  # To temporarily debug, the generated image can be displayed directly
        return im, code

    def draw_lines(self, draw, num, width, height):
        """
        draw interference lines
        :param draw: The image object
        :param num: The number of interference lines
        :param width: The width of the image
        :param height: The height of the image
        :return:
        """
        for num in range(num):
            x1 = random.randint(0, width / 2)
            y1 = random.randint(0, height / 2)
            x2 = random.randint(0, width)
            y2 = random.randint(height / 2, height)
            draw.line(((x1, y1), (x2, y2)), fill='black', width=2)

class EmailCode:
    def send_email(self,receiver, ecode):
        # Try to write the basic information elsewhere so that it can be easily referenced
        sender_email="fsyaxx@gmail.com"
        sender_password="zlgpgpelypewfwyy"
        # create the message object
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver
        msg['Subject'] = Header('Verification Code', 'utf-8')
        content = f"Your email verification code is：<span style='color: red; font-size: 20px;'>{ecode}</span>"
        # add the body to the message
        msg.attach(MIMEText(content, 'html', 'utf-8'))

        # create the SMTP connection
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            # start the TLS connection
            smtp.starttls()

            # login to the Gmail account
            smtp.login(sender_email, sender_password)

            # send the message
            smtp.send_message(msg)

        print('Email sent successfully')

    # def send_email(self, receiver, ecode):
    #     """发送邮件"""
    #     sender = 'Brenda <fsyaxx@gmail.com>'  # 邮箱账号和发件者签名
    #
    #     # 定义发送邮件的内容，支持HTML和CSS样式
    #     content = f"您的邮箱验证码为：<span style='color: red; font-size: 20px;'>{ecode}</span>"
    #     message = MIMEText(content, 'html', 'utf-8')  # 实例化邮件对象，并指定邮件的关键信息
    #     # 指定邮件的标题，同样使用utf-8编码
    #     message['Subject'] = Header('验证码', 'utf-8')
    #     message['From'] = sender
    #     message['To'] = receiver
    #
    #     smtpObj = SMTP_SSL('smtp.gmail.com')  # QQ邮件服务器的链接
    #     # zlgpgpelypewfwyy
    #     smtpObj.login(user='fsyaxx@gmail.com', password='zlgpgpelypewfwyy')  # 通过自己的邮箱账号和获取到的授权码登录QQ邮箱
    #
    #     # 指定发件人、收件人和邮件内容
    #     smtpObj.sendmail(sender, receiver, str(message))
    #     smtpObj.quit()


    def gen_email_code(self):
        str = random.sample(string.ascii_letters + string.digits, 6)
        return ''.join(str)

code,img=ImageCode().draw_verify_code()
print(img)
# email=EmailCode()
# email.send_email(receiver="fsy_118@163.com",ecode="123")