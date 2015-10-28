import re


class StandardiserNoOutputException(Exception):
    pass


def get_standardiser(urn):
    return URN_STANDARDISERS.get(urn[:2], URN_STANDARDISERS["*"])


def normalise_standard_urn(urn):
    return format_urn(standardise_urn(urn))


def normalise_met_urn(urn):
    return format_met_urn(standardise_urn(urn))


def standardise_urn(urn):
    """
    Strips non-alphanumeric characters from given URN, and 
    capitalise any letter
    """
    output = re.sub(r"[\W_]+", "", urn).upper()

    if len(output) == 0:
        raise StandardiserNoOutputException("Standardised URN is blank")

    return output


def format_urn(urn):
    """
    Inserts slashes in a standardised URN
    """
    return urn[:2] + "/" + urn[2:4] + "/" + urn[4:-2] + "/" + urn[-2:]


def format_met_urn(urn):
    return urn[:10] + "/" + urn[10:12] + "/" + urn[12:]


URN_STANDARDISERS = {
    "02": normalise_met_urn,
    "*": normalise_standard_urn
}
