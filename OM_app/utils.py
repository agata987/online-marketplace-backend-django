import string
import random
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import logging


def get_rundom_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join((random.choice(letters_and_digits) for i in range(length)))


def send_verification_email(to, verification_hash, domain, id):
    # verification link
    relative_link = reverse('verify-email')
    abs_url = 'https://' + domain + relative_link + '?hash=' + verification_hash + '?id=' + str(id)

    # email
    subject = 'Witaj na Online Marketplace, potwierdź swój adres email.'

    text_content = 'Aby dokończyć rejestrację, potwierdź swój adres email za pomocą poniższego linku:\n' + abs_url
    html_content = render_to_string('verify_email.html')
    html_content = html_content.replace('$(verify_link)', abs_url)

    email = EmailMultiAlternatives(subject, text_content, to=[to])
    email.attach_alternative(html_content, 'text/html')

    try:
        email.send(fail_silently=False)
    except Exception as e:
        logging.error('exception when sending an email to ' + to + " : " + str(e))
