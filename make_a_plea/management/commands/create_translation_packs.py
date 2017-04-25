"""
create_translation_packs
========================

"""

import datetime
import os
import shutil
import tempfile 
import zipfile
from subprocess import call

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils import translation
from django.utils.translation import ugettext


ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__))))

# Dummy data for the templates
DATA = {
    "name": "Anne Other",
    "urn": "00/00/0000000",
    "court": {"court_name": "Dummy test court"},
    "fines": [123.99, 124.49],
    "total": 444.44,
    "pay_by": datetime.datetime.utcnow(),
    "endorsements": ["SP30", "SP40"],
    "payment_details": ""
}

# It would be better to get these from the templates we process
# but origin seems to always be None. Perhaps due to middleware or
# custom template loaders?
TEMPLATES = [
    "apps/result/templates/emails/user_resulting.html",
    "apps/plea/templates/emails/user_plea_confirmation.html",
    "apps/plea/templates/emails/user_plea_confirmation_sjp.html",
    "apps/result/templates/emails/user_resulting.txt",
    "apps/plea/templates/emails/user_plea_confirmation.txt",
    "apps/plea/templates/emails/user_plea_confirmation_sjp.txt",
]

# Look for templates with these filenames
MESSAGE_NAMES = [
    "user_resulting",
    "user_plea_confirmation",
    "user_plea_confirmation_sjp",
    "admin_receipt_email",
]

# Search for templates with these extensions
MESSAGE_TYPES = ["txt", "html"]

# Search for templates with these path prefixes
MESSAGE_PREFIXES = [
    "email",
    "emails",
]

LANGUAGES = os.listdir(os.path.join(ROOT_DIR, "conf", "locale"))


# Make sure to use the latest messages
call([os.path.join(ROOT_DIR, "makemessages.sh")])
call_command("compilemessages")


def zipdir(path, ziph):
    """Write all files in path to zipfile handle"""
    abs_src = os.path.abspath(path)
    for root, dirs, files in os.walk(path):
        for filename in files:
            absname = os.path.abspath(os.path.join(root, filename))
            arcname = absname[len(abs_src) + 1:]
            ziph.write(absname, arcname)


class Command(BaseCommand):

    help = """
Create translation packs for translators. Run this command then send the
resulting zip files to the respective translators. The zip file contains .po
files, templates, example renderings and a coverletter that may serve as
documentation, style guide and remind us of any (e.g. grammatical) decisions.
Merging in the translator's work is not handled."""

    def handle(self, *args, **options):

        # Create a pack for each language
        for lang in LANGUAGES:
            tmp = tempfile.mkdtemp()
            for msg_name in MESSAGE_NAMES:
                for msg_type in MESSAGE_TYPES:
                    translation.activate(lang)
                    for msg_prefix in MESSAGE_PREFIXES:

                        # Include this template in this language
                        filename = "{0}/{1}.{2}".format(
                            msg_prefix,
                            msg_name,
                            msg_type,
                        )
                        try:
                            template = get_template(filename)
                        except TemplateDoesNotExist:
                            continue
                        else:
                            output = template.render(DATA)

                            with open(
                                os.path.join(
                                    tmp,
                                    "{}_{}.{}".format(
                                        lang,
                                        msg_name,
                                        msg_type)
                                ),
                                "wb",
                            ) as writefile:
                                writefile.write(output.encode("UTF-8"))

            # Include the original templates for context
            for template in TEMPLATES:
                shutil.copy(
                    template,
                    os.path.join(
                        tmp,
                        "{}.template".format(''.join(template.split("/")[-1:])),
                    ))

            # Include the appropriate .po file
            shutil.copyfile(
                os.path.join(
                    ROOT_DIR,
                    "conf",
                    "locale",
                    lang,
                    "LC_MESSAGES",
                    "django.po",
                ),
                os.path.join(
                    tmp,
                    "{}-django.po".format(lang),
                ),
            )

            # Include a covering letter
            with open(
                os.path.join(
                    tmp,
                    "coverletter.txt",
                ),
                "w",
            ) as coverletter:
                coverletter.write("""
Dear translators,

The word lists (django.po file) is for the strings to be translated. Pluralisation is also handled here.

The .template files show how the various email messages we use are constructed from the underlying word list.

The .txt and .html files are examples of the templates being processed and is what the user will see.

There is dummy data included in the processed templated. In case it is not obvious, the data is provided in the data.json file.

While it may be possible to incorporate some further rules of grammar in the templates, it would be preferable to translate the string in a way which minimises the use of these rules while still preserving a faithful and high quality translation.

""")

            # Compress for the translators
            with zipfile.ZipFile(
                '{}_translation_files.zip'.format(lang),
                'w',
                 zipfile.ZIP_DEFLATED,
            ) as zipf:
                zipdir(tmp, zipf)

            # Clean up safely
            if tmp.startswith(tempfile.gettempdir()):
                shutil.rmtree(tmp)
            else:
                raise Exception(
                    "Tempdir not in tempfile location, not cleaning up")
