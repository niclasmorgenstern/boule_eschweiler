# Generated by Django 5.0.3 on 2024-05-02 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boule', '0002_remove_player_name_player_first_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='last_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterUniqueTogether(
            name='player',
            unique_together={('first_name', 'last_name')},
        ),
    ]
