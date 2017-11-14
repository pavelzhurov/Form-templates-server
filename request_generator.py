import random
import re
import string

names = ("client_phone", "client_mail", "client_name",
         "worker_phone", "worker_mail", "worker_name",
         "purchase_information", "purchase_date",
         "company_open_date", "company_close_date",
         "company_phone", "company_name")


def generate_request(max_number_of_fields=12):
    """ Return string for post request """
    # Max number of fields shouldn't be more then 12
    size = int(random.random()*max_number_of_fields) + 1
    request = ""
    keys = random.choices(names, k=size)
    for key in keys:
        value = None
        if re.match(".*_phone", key):
            value = generate_phone()
        elif re.match(".*_mail", key):
            value = generate_email()
        elif re.match(".*_date", key):
            value = generate_date()
        elif re.match(".*_information", key) or re.match(".*_name", key):
            value = generate_text()
        request += key + "=" + value + "&"
    # Cut last '&'
    return request[:-1]


def generate_phone():
    # +7 xxx xxx xx xx
    random_phone = tuple(str(int(random.random()*10)) for _ in range(10))
    return "+7 {}{}{} {}{}{} {}{} {}{}".format(*random_phone)


def generate_date():
    # DD.MM.YYYY
    # Year since 1970
    year = int(random.random()*47) + 1970
    month = int(random.random()*12) + 1
    if month != 2:
        if (month < 8 and month % 2 == 1) or (month > 7 and month % 2 == 0):
            day = str(int(random.random()*31))
        else:
            day = str(int(random.random()*30))
    else:
        if ((year % 4 == 0) and (year % 100 != 0)) or (year % 400 == 0):
            day = str(int(random.random()*29))
        else:
            day = str(int(random.random()*28))
    if len(day) == 1:
        day = "0" + day
    if month < 10:
        month = "0" + str(month)
    else:
        month = str(month)
    return "{}.{}.{}".format(day, month, str(year))


def generate_email(max_part_size=8):
    # user@company_name.domen
    if max_part_size > 63:
        raise TypeError("Impossible domain size")
    symbols = string.ascii_lowercase + string.digits
    parts_sizes = [int(random.random()*max_part_size) + 1 for _ in range(3)]
    email_parts = tuple(''.join(random.choices(symbols, k=size)) for size in parts_sizes)
    return "{}@{}.{}".format(*email_parts)


def generate_text(name=False, max_text_size=120):
    # Max size 120 symbols if text and 8 if name
    if name and max_text_size > 8:
        max_text_size = 8
        symbols = string.ascii_lowercase
    else:
        symbols = string.ascii_lowercase + string.digits + string.ascii_uppercase
    if max_text_size > 120:
        raise TypeError("Invalid text size: too big!")
    size = int(random.random()*max_text_size) + 1
    result = ''.join(random.choices(symbols, k=size))
    return result.capitalize()
