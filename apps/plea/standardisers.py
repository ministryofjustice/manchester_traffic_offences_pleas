import re


class StandardiserNoOutputException(Exception):
    pass


def format_for_region(urn):
    format = URN_FORMATTERS.get(urn[:2], URN_FORMATTERS["*"])
    return format(standardise_urn(urn))


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
    return urn

URN_FORMATTERS = {"02": format_met_urn,
                  "*": format_urn}
