"""
This is a quick and dirty script to generate lines for feature files with
complex example scenarios. Consider re-factoring and importing the copied
logic from the cucumber fixture generator.
"""

import os


filename = "duplicate_urns.feature"
root = os.path.dirname(__file__)
with open("out.feature", "w") as outfile:
    outfile.write("        |     urn     | init_type | result  | OU_null | sent   | name_match | postcode_match | dob_match  | strict  | OU_match  | personal |\n")
    for init_type in ["J", "R", "O"]:
        for OU_null in [True, False]:
            for sent in [True, False]:
                for name_match in [True, False]:
                    for postcode_match in [True, False]:
                        for dob_match in [True, False]:
                            for strict in [True, False]:
                                for OU_match in [True, False]:
                                    for personal in [True, False]:
                                        init_type_weighting = \
                                            int("J" in init_type) * 1 + \
                                            int("R" in init_type) * 2 + \
                                            int("O" in init_type) * 4
                                        urn_part = sum([
                                            init_type_weighting * 256,
                                            OU_null * 128,
                                            sent * 64,
                                            name_match * 32,
                                            postcode_match * 16,
                                            dob_match * 8,
                                            strict * 4,
                                            OU_match * 2,
                                            personal * 1,
                                        ])
                                        urn = "11{court}{urn_part:05d}17".format(
                                            urn_part=urn_part,
                                            court="AA" if strict else "BB",
                                        )
                                        parts = []
                                        parts.append("        ")
                                        parts.append(
                                            " {0}{1}{2:05d}17 ".format(
                                                "11",
                                                "AA" if strict else "BB",
                                                urn_part,
                                            )
                                        )
                                        parts.append(
                                            " {}         ".format(
                                                init_type,
                                            )
                                        )
                                        parts.append(
                                            " success "
                                        )
                                        parts.append(
                                            " {}   ".format(
                                                "true " if OU_null else "false",
                                            )
                                        )
                                        parts.append(
                                            " {}  ".format(
                                                "true " if sent else "false",
                                            )
                                        )
                                        parts.append(
                                            " {}      ".format(
                                                "true " if name_match else "false",
                                            )
                                        )
                                        parts.append(
                                            " {}          ".format(
                                                "true " if postcode_match else "false",
                                            )
                                        )
                                        parts.append(
                                            " {}      ".format(
                                                "true " if dob_match else "false",
                                            )
                                        )
                                        parts.append(
                                            " {}   ".format(
                                                "true " if strict else "false",
                                            )
                                        )
                                        parts.append(
                                            " {}     ".format(
                                                "true " if OU_match else "false"
                                            )
                                        )
                                        parts.append(
                                            " {}    |".format(
                                                "true " if personal else "false",
                                            )
                                        )

                                        outfile.write("|".join(parts) + "\n")
