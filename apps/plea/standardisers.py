import re

class StandardiserNoOutputException(Exception):
    pass

def standardise_urn(urn):
    """
    Strips non-alphanumeric characters from given URN, and 
    capitalise any letter
    """
    output = re.sub(r"[\W_]+", "", urn).upper()

    if len(output) == 0:
        raise StandardiserNoOutputException("Standardised URN is blank")

    return output


def slashify_urn(urn):
    """
    Inserts slashes in a standardised URN
    """
    return urn[:2] + "/" + urn[2:4] + "/" + urn[4:-2] + "/" + urn[-2:]
