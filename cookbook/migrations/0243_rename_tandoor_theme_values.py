from django.db import migrations, models


def rename_theme_values(apps, schema_editor):
    UserPreference = apps.get_model('cookbook', 'UserPreference')
    Space = apps.get_model('cookbook', 'Space')
    UserPreference.objects.filter(theme='TANDOOR').update(theme='STILLROOM')
    UserPreference.objects.filter(theme='TANDOOR_DARK').update(theme='STILLROOM_DARK')
    Space.objects.filter(space_theme='TANDOOR').update(space_theme='STILLROOM')
    Space.objects.filter(space_theme='TANDOOR_DARK').update(space_theme='STILLROOM_DARK')


def restore_theme_values(apps, schema_editor):
    UserPreference = apps.get_model('cookbook', 'UserPreference')
    Space = apps.get_model('cookbook', 'Space')
    UserPreference.objects.filter(theme='STILLROOM').update(theme='TANDOOR')
    UserPreference.objects.filter(theme='STILLROOM_DARK').update(theme='TANDOOR_DARK')
    Space.objects.filter(space_theme='STILLROOM').update(space_theme='TANDOOR')
    Space.objects.filter(space_theme='STILLROOM_DARK').update(space_theme='TANDOOR_DARK')


class Migration(migrations.Migration):

    dependencies = [
        ('cookbook', '0242_space_household_setup_completed'),
    ]

    operations = [
        migrations.RunPython(rename_theme_values, restore_theme_values),
        migrations.AlterField(
            model_name='space',
            name='space_theme',
            field=models.CharField(
                choices=[('BLANK', '-------'), ('STILLROOM', 'Stillroom'), ('BOOTSTRAP', 'Bootstrap'), ('DARKLY', 'Darkly'), ('FLATLY', 'Flatly'), ('SUPERHERO', 'Superhero'),
                         ('STILLROOM_DARK', 'Stillroom Dark (INCOMPLETE)')],
                default='BLANK',
                max_length=128
            ),
        ),
        migrations.AlterField(
            model_name='userpreference',
            name='theme',
            field=models.CharField(
                choices=[('STILLROOM', 'Stillroom'), ('BOOTSTRAP', 'Bootstrap'), ('DARKLY', 'Darkly'), ('FLATLY', 'Flatly'), ('SUPERHERO', 'Superhero'),
                         ('STILLROOM_DARK', 'Stillroom Dark (INCOMPLETE)')],
                default='STILLROOM',
                max_length=128
            ),
        ),
    ]
