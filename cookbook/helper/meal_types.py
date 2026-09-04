from datetime import time

from django.utils.translation import gettext as _


DEFAULT_MEAL_TYPES = (
    {'name': 'Breakfast', 'order': 0, 'time': time(8, 0), 'color': '#ddbf86'},
    {'name': 'Lunch', 'order': 1, 'time': time(12, 0), 'color': '#82aa8b'},
    {'name': 'Dinner', 'order': 2, 'time': time(18, 0), 'color': '#385f84'},
)


def ensure_default_meal_types(space, user):
    """Create Breakfast/Lunch/Dinner for a space that has no meal types yet."""
    from cookbook.models import MealType

    if MealType.objects.filter(space=space).exists():
        return

    for defaults in DEFAULT_MEAL_TYPES:
        MealType.objects.get_or_create(
            space=space,
            name=_(defaults['name']),
            defaults={
                'created_by': user,
                'order': defaults['order'],
                'time': defaults['time'],
                'color': defaults['color'],
            },
        )
