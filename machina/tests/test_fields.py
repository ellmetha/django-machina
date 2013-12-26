# -*- coding: utf-8 -*-

# Standard library imports
import os

# Third party imports
from django.conf import settings
from django.core.files import File
from django.test import TestCase
from django.utils.six import StringIO

# Local application / specific library imports
from machina.core.compat import PILImage as Image
from machina.tests import RESIZED_IMAGE_HEIGHT
from machina.tests import RESIZED_IMAGE_WIDTH
from machina.tests import TestableModel


class ExtendedImageFieldTestCase(TestCase):
    def setUp(self):
        # Set up some images used for doing image tests
        TEST_ROOT = os.path.abspath(os.path.dirname(__file__))
        settings.MEDIA_ROOT = os.path.join(TEST_ROOT, 'testdata/media/')

        # Fetch an image aimed to be resized
        f = open(settings.MEDIA_ROOT + "/to_be_resized_image.png", "rb")
        self.to_be_resized_image = File(f)

    def tearDown(self):
        self.to_be_resized_image.close()
        tests = TestableModel.objects.all()
        for test in tests:
            try:
                test.resized_image.delete()
            except:
                pass

    def test_resized_image_saving(self):
        # Setup
        test = TestableModel()
        # Run
        field = test._meta.get_field('resized_image')
        field.save_form_data(test, self.to_be_resized_image)
        test.save()
        # Check
        image = Image.open(StringIO(test.resized_image.read()))
        self.assertEqual(image.size, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))
