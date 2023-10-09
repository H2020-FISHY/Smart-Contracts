from django.db import models

class Handler(models.Model):
    link_id = models.CharField(primary_key=True, db_index=True, editable=False, max_length=255)
    ipfs_link = models.CharField(max_length=255)