from machina.apps.forum.abstract_models import AbstractForum
from machina.core.db.models import model_factory


Forum = model_factory(AbstractForum)
