# Generated by Django 4.0.3 on 2022-04-15 04:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyplan', '0007_alter_freelance_instructor_pilots_dat_prov'),
    ]

    operations = [
        migrations.RenameField(
            model_name='instructors',
            old_name='PODRAZ',
            new_name='GROUP',
        ),
        migrations.AddField(
            model_name='instructors',
            name='TYPE_ARCRAFT',
            field=models.CharField(max_length=200, null=True),
        ),
    ]