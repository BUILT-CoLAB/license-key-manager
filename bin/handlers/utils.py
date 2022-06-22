import re

def validateMultiple_NEP(name, email, phoneNumber):
    sequence = [ (validateName, name), (validateEmail, email), (validatePhone, phoneNumber)]
    messageErrors = ""
    for method, parameter in sequence:
        try:
            method(parameter)
        except Exception as failure:
            messageErrors += "\n" + str(failure)
    return messageErrors


def validateEmail(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if( not re.fullmatch(regex, email) ):
        raise Exception("- Invalid Email")

def validatePhone(phoneNumber):
    if( not str(phoneNumber).isnumeric() ):
        raise Exception("- Invalid Phone Number")

def validateName(name):
    if( not str(name).replace(' ', '').isalpha() ):
        raise Exception("- Invalid Name")