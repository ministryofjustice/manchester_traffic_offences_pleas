import os
from ftplib import FTP

import requests

from apps.plea.models import Case


__all__ = ("check_url", "check_ftp", "check_address", "check_mandrill", "check_database")


def check_url(url, timeout=3):
    """
    Verify that a url exists and returns a 200 status
    in a reasonable time period.
    """

    try:
        response = requests.get(url, timeout=timeout, verify=False)
    except requests.exceptions.RequestException:
        return False
    else:
        if response.status_code != 200:
            return False

    return True


def check_ftp(host, port, timeout=3):
    """
    Verify that we can make a connection to an FTP server
    """

    ftp = FTP()

    try:
        ftp.connect(host, port, timeout)

    except Exception:
        return False
    else:
        ftp.close()

    return True


def check_address(address):
    """
    Check that an address can be ICMP pinged
    """

    if os.system("ping -c 1 {}".format(address)) == 0:
        return True
    else:
        return False


def check_mandrill():
    """
    Verify that we can connect to Mandrill
    """

    return check_address("smtp.mandrillapp.com")


def check_database():
    """
    Can we access the database?
    """

    try:
        Case.objects.all()
    except Exception:
        return False

    return True