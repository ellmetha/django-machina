"""
    Django-machina
    ==============

    Django-machina is a Django forum engine for building powerful community driven websites. It
    offers a full-featured yet very extensible forum solution.

"""

import os


# Main Machina static directory.
MACHINA_MAIN_STATIC_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'static/machina/build',
)

# Main Machina template directory.
MACHINA_MAIN_TEMPLATE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'templates/machina',
)
