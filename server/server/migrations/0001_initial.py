# Generated by Django 3.2.16 on 2022-10-11 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Handler',
            fields=[
                ('link_id', models.IntegerField(db_index=True, editable=False, primary_key=True, serialize=False)),
                ('ipfs_link', models.CharField(max_length=255)),
            ],
        ),
    ]
