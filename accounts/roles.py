from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


def create_default_roles(**kwargs):
    groups = {name: Group.objects.get_or_create(name=name)[0] for name in [
        'dg', 'rh', 'actuaire', 'commercial', 'redacteur', 'gestionnaire', 'comptable'
    ]}

    try:
        user_ct = ContentType.objects.get(app_label='auth', model='user')
        profile_ct = ContentType.objects.get(app_label='accounts', model='userprofile')
        product_ct = ContentType.objects.get(app_label='catalog', model='product')
        coverage_ct = ContentType.objects.get(app_label='catalog', model='coverage')
        insured_ct = ContentType.objects.get(app_label='crm', model='insured')
        policy_ct = ContentType.objects.get(app_label='underwriting', model='policy')
        complaint_ct = ContentType.objects.get(app_label='complaints', model='complaint')
        claim_ct = ContentType.objects.get(app_label='claims', model='claim')
        attachment_ct = ContentType.objects.get(app_label='claims', model='attachment')
        payment_ct = ContentType.objects.get(app_label='finance', model='payment')
        receipt_ct = ContentType.objects.get(app_label='finance', model='receipt')
        premium_ct = ContentType.objects.get(app_label='finance', model='premium')
    except ContentType.DoesNotExist:
        return

    view_perms = Permission.objects.filter(codename__startswith='view_')
    groups['dg'].permissions.add(*view_perms)

    rh_perms = Permission.objects.filter(content_type=user_ct)
    groups['rh'].permissions.add(*rh_perms)
    change_profile = Permission.objects.get(content_type=profile_ct, codename='change_userprofile')
    groups['rh'].permissions.add(change_profile)

    act_perms = Permission.objects.filter(content_type__in=[product_ct, coverage_ct])
    groups['actuaire'].permissions.add(*act_perms)

    comm_codes = [
        'add_insured', 'change_insured', 'view_insured',
        'add_policy', 'change_policy', 'view_policy',
        'add_complaint', 'view_complaint'
    ]
    comm_perms = Permission.objects.filter(codename__in=comm_codes)
    groups['commercial'].permissions.add(*comm_perms)

    red_codes = ['add_claim', 'view_claim', 'add_attachment', 'view_attachment']
    red_perms = Permission.objects.filter(codename__in=red_codes)
    groups['redacteur'].permissions.add(*red_perms)

    gest_codes = [
        'view_claim', 'change_claim', 'approve_claim', 'reject_claim',
        'view_complaint', 'answer_complaint', 'close_complaint'
    ]
    gest_perms = Permission.objects.filter(codename__in=gest_codes)
    groups['gestionnaire'].permissions.add(*gest_perms)

    comp_codes = ['view_payment', 'pay_claim', 'view_receipt', 'receive_premium', 'view_premium']
    comp_perms = Permission.objects.filter(codename__in=comp_codes)
    groups['comptable'].permissions.add(*comp_perms)
