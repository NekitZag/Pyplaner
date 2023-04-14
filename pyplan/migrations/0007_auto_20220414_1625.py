# Generated by Django 3.2.12 on 2022-04-14 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyplan', '0006_freelance_instructor_pilots_freelance_instructor_pilots_check_krs_according_staff_schedule_krs_lis_a'),
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
        migrations.AlterField(
            model_name='freelance_instructor_pilots',
            name='DAT_PROV',
            field=models.DateTimeField(null=True),
        ),
    ]
