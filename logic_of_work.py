import email

import requests
import time
import smtplib
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from email.mime.base import MIMEBase
from email import encoders

class logic():
    @staticmethod
    def send_message(sender_email,senders_password,receiver_email,title,body,server="smtp.mail.ru",port=587,image=None):
        message = MIMEMultipart()
        message["To"] = receiver_email
        message["From"] = sender_email
        message["Subject"] = title
        message.attach(MIMEText(body))
        """Если человек задал путь к изображению """
        if image is not None:
            with open(image, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={image.split("\\")[-1]}"
            )
            message.attach(part)
        try:
            server_connect = smtplib.SMTP(server,port)
            server_connect.starttls()
            server_connect.login(sender_email,senders_password)
            text = message.as_string()
            server_connect.sendmail(sender_email,receiver_email,text)
            print("Сообщение успешно доставлено")
        except smtplib.SMTPException as e:
            print(f"Ошибка при отправке письма : {e}")
        finally:
            server_connect.quit()

    @staticmethod
    def choose_for_continue():
        choose = input(
                       "1 - Да\n"
                       "Любой другой символ - нет\n")
        return choose == "1"


    @staticmethod
    def try_to_connect(url,timeout,interval):
        start = time.time()
        while time.time()-start<timeout:
            try:
                response=requests.get(url)
                if response.status_code==200:
                    print("Подключение успешно!")
                    return True
            except requests.exceptions.ConnectionError as ce:
                print(f"Ошибка соединения: {ce}")
            except requests.exceptions.RequestException as e:
                print(f"Ошибка : {e}")
            print(f"Следующая попытка подключения через : {interval} секунд")
            time.sleep(interval)
        return False

    """Проверка правильности введенного IMAP - сервера"""
    @staticmethod
    def connect_to_imap_server(server,port):
        try:
            mail=imaplib.IMAP4_SSL(server,port)
            return mail
        except Exception as e:
            print(f"Ошибка подключения к серверу: {e}")
            return None

    """Проверка имеются ли новые сообщения и их чтение"""
    @staticmethod
    def check_new_messages():
        imap_address = input("Введите адрес IMAP-сервера (например, imap.mail.ru): ")
        imap_port = int(input("Введите порт IMAP-сервера (обычно 993): "))
        mail = logic.connect_to_imap_server(imap_address,imap_port)
        if mail is not None:
            email_address = input("Введите ваш почтовый ящик: ")
            email_password = input("Пароль от почтового ящика: ")
            try:
                mail.login(email_address,email_password)
            except Exception as e:
                print(f"Ошибка подключения : {e}")
            else:
                mail.select("INBOX")
                status, message = mail.search(None,"UNSEEN")
                if len(message[0]) == 0:
                    print("Новых сообщений нет")
                else:
                    print("Имеются новые непрочитанные сообщения!")
                    print("Желаете ли вы прочитать сообщения: ")
                    if logic.choose_for_continue():
                        for id in message[0].split():
                            status, msg_data = mail.fetch(id,"(RFC822)")
                            msg = email.message_from_bytes(msg_data[0][1])
                            if msg.is_multipart():
                                for part in msg.walk():
                                    content_type = part.get_content_type()
                                    content_disposition = str(part.get("Content-disposition"))
                                    if "attachment" in content_disposition:
                                        continue
                                    try:
                                        """Убираем html код из сообщения и достаем только текст"""
                                        body = part.get_payload(decode=True).decode()
                                        if content_type == "text/html":
                                            temp = BeautifulSoup(body,"html.parser")
                                            body = temp.get_text()
                                        print(body.strip())
                                    except:
                                        pass
                            else:
                                content_type = msg.get_content_type()
                                body = msg.get_payload(decode=True).decode()
                                if content_type == "text/html":
                                    temp = BeautifulSoup(body,"html.parser")
                                    body = temp.get_text()
                                print(body.strip())
                            print("Желаете ли вы продолжить чтение ?")
                            if not logic.choose_for_continue():
                                break
            finally:
                mail.logout()

    @staticmethod
    def input_data():
        sender_email = input("Почта отправителя: ")
        senders_password = input("Пароль отправителя: ")
        receiver_email = input("Почта получателя: ")
        title = input("Заголовок сообщения: ")
        body = input("Текст сообщения: ")
        smtp_address = input("Введите адрес SMTP-сервера (по умолчанию smtp.mail.ru): ")
        smtp_port = int(input("Введите порт SMTP-сервера (по умолчанию 587): "))
        return sender_email,senders_password,receiver_email,title,body,smtp_address,smtp_port

    @staticmethod
    def choosing_an_action():
        choose = input("Пожалуйста, выберите операцию, которую хотите произвести:\n"
                       "1.Отправить текстовое сообщение по почте\n"
                       "2.Отправить сообщение с изображением\n"
                       "3.Проверить сайт на доступность с заданным интервалом времени\n"
                       "4.Проверить наличие новых сообщений на почте\n"
                       "5.Закончить работу\n")
        if choose == "1":
            data = logic.input_data()
            logic.send_message(data[0],data[1],data[2],data[3],data[4],data[5],data[6])
        elif choose == "2":
            data = logic.input_data()
            image = input("Введите путь к изображению (используйте либо двойной \\, либо / ): ")
            logic.send_message(data[0],data[1],data[2],data[3],data[4],data[5],data[6],image)
        elif choose == "3":
            url = input("Введите url адрес: ")
            timeout = int(input("Промежуток времени (в секундах) в течении которого нужно подключаться: "))
            interval = int(input("Интервал (в секундах) между подключениями: "))
            if not logic.try_to_connect(url,timeout,interval):
                data = logic.input_data()
                print("Оповещение уже у вас на почте")
                logic.send_message(data[0],data[1],data[2],data[3],data[4],data[5],data[6])
        elif choose == "4":
            logic.check_new_messages()
        elif choose == "5":
            return False
        else:
            print("Некорректная операция, попробуйте еще раз")
        return True
