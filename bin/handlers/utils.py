from flask import render_template, request
import re

def validateMultiple_Customer(name, email, phoneNumber):
    sequence = [ (validateName, name), (validateEmail, email), (validatePhone, phoneNumber)]
    return validateSequence(sequence)

def validateMultiple_Admin(username, password, email):
    sequence = [ (validateUsername, username), (validatePassword, password), (validateEmail, email)]
    return validateSequence(sequence)

def validateSequence(sequence):
    messageErrors = ""
    for method, parameter in sequence:
        try:
            method(parameter)
        except Exception as failure:
            messageErrors += "\n" + str(failure)
    return messageErrors



# #######################################################################################
# ############## VALIDATIONS
# #######################################################################################

def validateUsername(username):
    if( len(username) == 0 or ' ' in str(username) ):
        raise Exception("- Invalid username")

def validatePassword(password):
    if( len(password) < 10 ):
        raise Exception("- Invalid password")

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




# #######################################################################################
# ############## MISC
# #######################################################################################

def render404(mainMessage = None, subMessage = None):
    mainMessage = "Page not found" if mainMessage == None else mainMessage
    subMessage = "Sorry, but the page you are looking for does not exist ..." if subMessage == None else subMessage
    return render_template('404.html', mode = request.cookies.get('mode'), main = mainMessage, sub = subMessage)