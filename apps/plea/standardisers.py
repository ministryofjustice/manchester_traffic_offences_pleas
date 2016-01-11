import re


class StandardiserNoOutputException(Exception):
    pass


def format_for_region(urn):
    format = URN_FORMATTERS.get(urn[:2], URN_FORMATTERS["*"])
    return format(standardise_urn(urn))


def standardise_postcode(postcode):
    return re.sub(r"[\W_]+", "", postcode).upper()


def standardise_urn(urn):
    """
    Strips non-alphanumeric characters from given URN, and
    capitalise any letter. If any regional variations are
    available URN_STANDARDISERS it also applies them.

    """
    output = re.sub(r"[\W_]+", "", urn).upper()

    regional_standardiser = URN_STANDARDISERS.get(output[:2], None)

    if regional_standardiser:
        output = regional_standardiser(output)

    if len(output) == 0:
        raise StandardiserNoOutputException("Standardised URN is blank")

    return output


def standardise_gmp_urn(urn):
    double_zero = re.compile("06([a-zA-Z]{2})00(.*)")
    if double_zero.match(urn) and len(double_zero.match(urn).groups()[1]) > 5:
        return re.sub(double_zero, "06\g<1>\g<2>", urn)
    else:
        return urn


def format_urn(urn):
    """
    Inserts slashes in a standardised URN
    """
    return urn[:2] + "/" + urn[2:4] + "/" + urn[4:-2] + "/" + urn[-2:]


def format_gmp_urn(urn):
    if len(urn[4:-2]) == 5:
        return urn[:2] + "/" + urn[2:4] + "/00" + urn[4:-2] + "/" + urn[-2:]
    return urn[:2] + "/" + urn[2:4] + "/" + urn[4:-2] + "/" + urn[-2:]


def format_met_urn(urn):
    return urn


URN_STANDARDISERS = {"06": standardise_gmp_urn}
URN_FORMATTERS = {"02": format_met_urn,
                  "06": format_gmp_urn,
                  "*": format_urn}
