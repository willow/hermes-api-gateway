from django.utils import timezone
from src.aggregates.potential_agreement.models import PotentialAgreement
from src.aggregates.potential_agreement.services import potential_agreement_factory


def get_potential_agreement(potential_agreement_id):
  return PotentialAgreement.objects.get(potential_agreement_id=potential_agreement_id)


def save_or_update(agreement):
  agreement.save(internal=True)


def create_potential_agreement(potential_agreement_name, potential_agreement_artifacts, potential_agreement_user_id):
  agreement = potential_agreement_factory.create_potential_agreement(potential_agreement_name,
                                                                     potential_agreement_artifacts,
                                                                     potential_agreement_user_id)
  save_or_update(agreement)
  return agreement


def get_potential_agreements_with_due_expiration_alert():
  ret_val = PotentialAgreement.objects.filter(
    potential_agreement_expiration_alert_date__lte=timezone.now(),
    potential_agreement_expiration_alert_enabled=True,
    potential_agreement_expiration_alert_created=False
  )
  return ret_val


def get_potential_agreements_with_due_outcome_notice_alert():
  ret_val = PotentialAgreement.objects.filter(
    potential_agreement_outcome_notice_alert_date__lte=timezone.now(),
    potential_agreement_outcome_notice_alert_enabled=True,
    potential_agreement_outcome_notice_alert_created=False
  )
  return ret_val
