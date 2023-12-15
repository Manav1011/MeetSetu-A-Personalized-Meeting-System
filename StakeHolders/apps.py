from django.apps import AppConfig


class StakeholdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'StakeHolders'

    def ready(self) -> None:
        import StakeHolders.signals