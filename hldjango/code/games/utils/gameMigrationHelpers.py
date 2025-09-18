from django.conf import settings
from django.utils import timezone

# python modules
import pathlib
import datetime
import os



# backfill missing fields for game files
# note this must remain stable forever
def backfill_gamefile_metadata_fileNameSizeDate(apps, schema_editor):
    MyModel = apps.get_model("games", "gamefile")

    for obj in MyModel.objects.all():
        if obj.filefield and not obj.fileName:
            path = obj.filefield.name
            full_path = os.path.join(settings.MEDIA_ROOT, path)
            obj.fileName = pathlib.Path(path).name.lower()

            try:
                stat = os.stat(full_path)
                obj.fileSize = stat.st_size
                naive_dt = datetime.datetime.fromtimestamp(stat.st_mtime)
                obj.fileDate = timezone.make_aware(naive_dt, timezone.get_current_timezone())
            except (OSError, FileNotFoundError):
                obj.fileSize = None
                obj.fileDate = None
                print("ERROR: FAILED TO BACKFILL GAME FILE NAME/DATE/SIZE; FILE NOT FOUND (might be just a deleted file needing reconciling): '{}' mapped to '{}'".format(path, full_path))

            obj.save()
