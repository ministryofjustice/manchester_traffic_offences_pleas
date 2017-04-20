import os
import datetime
import tempfile 
import shutil
import zipfile

from django.core.management.base import BaseCommand
from django.template import TemplateDoesNotExist #, loader
from django.template.loader import get_template
from django.utils import translation
from django.utils.translation import ugettext


root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Dummy data for the templates
data = {
    "name": "Anne Other",
    "urn": "00/00/0000000",
    "court": {"court_name": "Dummy test court"},
    "fines": [123.99, 124.49],
    "total": 444.44,
    "pay_by": datetime.datetime.utcnow(),
    "endorsements": ["SP30", "SP40"],
    "payment_details": ""
}


def zipdir(path, ziph):
    """Write all files in path to zipfile handle"""
    abs_src = os.path.abspath(path)
    for root, dirs, files in os.walk(path):
        for filename in files:
            absname = os.path.abspath(os.path.join(root, filename))
            arcname = absname[len(abs_src) + 1:]
            ziph.write(absname, arcname)


class Command(BaseCommand):
    help = "Create translation zip packs containing po files, templates, example renderings and a coverletter"

    def handle(self, *args, **options):
        for lang in os.listdir(os.path.join(root_dir, "conf", "locale")):
            tmp = tempfile.mkdtemp()

            for msg_purpose in [
                "user_resulting",
                "user_plea_confirmation",
                "user_plea_confirmation_sjp",
                "admin_receipt_email"
            ]:
                for msg_type in ["txt", "html"]:

                    translation.activate(lang)

                    try:
                        filename = "email/{}.{}".format(msg_purpose, msg_type)
                        tmplt = get_template(filename)
                    except TemplateDoesNotExist:
                        try:
                            filename = "emails/{}.{}".format(msg_purpose, msg_type)
                            tmplt = get_template(filename)
                        except TemplateDoesNotExist:
                            break
                    finally:
                        output = tmplt.render(data)

                    with open(
                        os.path.join(
                            tmp,
                            "{}_{}.{}".format(
                                lang,
                                msg_purpose,
                                msg_type)
                        ),
                        "wb",
                    ) as writefile:
                        writefile.write(output.encode("UTF-8"))

            # Django 1.7 has no origin.name, hard-coding for now
            for template in [
                "apps/result/templates/emails/user_resulting.html",
                "apps/plea/templates/emails/user_plea_confirmation.html",
                "apps/plea/templates/emails/user_plea_confirmation_sjp.html",
                "apps/result/templates/emails/user_resulting.txt",
                "apps/plea/templates/emails/user_plea_confirmation.txt",
                "apps/plea/templates/emails/user_plea_confirmation_sjp.txt",
            ]:
                shutil.copy(
                    template,
                    os.path.join(
                        tmp,
                        "{}.template".format(''.join(template.split("/")[-1:])),
                    ))

            # Include the appropriate .po file
            shutil.copyfile(
                os.path.join(
                    root_dir,
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
            with open(os.path.join(tmp, "coverletter.txt"), "w") as coverletter:
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
                raise Exception("Tempdir not in tempfile location, not cleaning up")
