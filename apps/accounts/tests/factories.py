import factory

from apps.accounts.models import User

DEFAULT_PASSWORD = "unaClaveSegura123"


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"persona{n}@example.com")
    full_name = factory.Faker("name", locale="es_AR")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", DEFAULT_PASSWORD)
        return model_class.objects.create_user(*args, password=password, **kwargs)
