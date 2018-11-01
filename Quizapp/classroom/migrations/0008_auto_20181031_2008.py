# Generated by Django 2.1.2 on 2018-11-01 03:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0007_auto_20181031_1336'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationalDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization_name', models.CharField(blank=True, max_length=255, unique=True)),
                ('organization_email', models.EmailField(blank=True, max_length=70, null=True, unique=True)),
                ('organization_description', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='PersonalDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('email', models.EmailField(blank=True, max_length=70, null=True, unique=True)),
                ('mobile', models.IntegerField()),
                ('organization_name', models.ForeignKey(default='nothing', on_delete=django.db.models.deletion.CASCADE, to='classroom.OrganizationalDetails')),
            ],
        ),
        migrations.DeleteModel(
            name='RecruiterDetails',
        ),
        migrations.AddField(
            model_name='job',
            name='organization_name',
            field=models.ForeignKey(default='nothing', on_delete=django.db.models.deletion.CASCADE, to='classroom.OrganizationalDetails'),
        ),
    ]
