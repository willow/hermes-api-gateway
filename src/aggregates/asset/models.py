from django.db import models, transaction
from django.conf import settings

from src.aggregates.asset.signals import created
from src.libs.common_domain.aggregate_base import AggregateBase
from src.libs.common_domain.models import Event

constants = settings.CONSTANTS
assets_root = constants.ASSETS_ROOT


class Asset(models.Model, AggregateBase):
  asset_id = models.CharField(max_length=8, unique=True)
  asset_path = models.CharField(max_length=2400)
  asset_content_type = models.CharField(max_length=2400)
  asset_original_name = models.CharField(max_length=2400)
  asset_system_created_date = models.DateTimeField()

  @classmethod
  def _from_attrs(cls, asset_id, asset_path, asset_content_type, asset_original_name, asset_system_created_date):
    ret_val = cls()

    if not asset_id:
      raise TypeError("asset_id is required")

    if not asset_path:
      raise TypeError("asset_path is required")

    if not asset_content_type:
      raise TypeError("asset_content_type is required")

    if not asset_original_name:
      raise TypeError("asset_original_name is required")

    if not asset_path:
      raise TypeError("asset_path is required")

    ret_val._raise_event(
      created,
      asset_id=asset_id, asset_path=asset_path, asset_content_type=asset_content_type,
      asset_original_name=asset_original_name, asset_system_created_date=asset_system_created_date
    )

    return ret_val

  @property
  def asset_signed_path(self, _asset_service=None):
    # this model is assuming the responsibility of figuring out the signed path but handing off that responsibility
    # to the asset service, using the double dispatch pattern.
    # https://lostechies.com/jimmybogard/2010/03/30/strengthening-your-domain-the-double-dispatch-pattern/
    if not _asset_service:
      from src.aggregates.asset.services import asset_service

      _asset_service = asset_service

    ret_val = _asset_service.get_signed_asset_path(self.asset_path)

    return ret_val

  def _handle_created_event(self, **kwargs):
    self.asset_id = kwargs['asset_id']
    self.asset_path = kwargs['asset_path']
    self.asset_content_type = kwargs['asset_content_type']
    self.asset_original_name = kwargs['asset_original_name']
    self.asset_system_created_date = kwargs['asset_system_created_date']

  def __str__(self):
    return 'Asset #' + str(self.asset_id) + ': ' + self.asset_original_name

  def save(self, internal=False, *args, **kwargs):
    if internal:
      with transaction.atomic():
        super().save(*args, **kwargs)

        for event in self._uncommitted_events:
          Event.objects.create(
            aggregate_name=self.__class__.__name__, aggregate_id=self.asset_id,
            event_name=event.event_fq_name, event_version=event.version, event_data=event.kwargs
          )

      self.send_events()
    else:
      from src.aggregates.asset.services import asset_service

      asset_service.save_or_update(self)
