# Generated by Django 4.0.3 on 2022-04-14 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyplan', '0006_freelance_instructor_pilots_freelance_instructor_pilots_check_krs_according_staff_schedule_krs_lis_a'),
    ]

    operations = [
        migrations.AlterField(
            model_name='freelance_instructor_pilots',
            name='DAT_PROV',
            field=models.DateTimeField(null=True),
        ),
    ]