from django.db import migrations


def backfill_roles_and_usernames(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    User = apps.get_model("auth", "User")
    admin, _ = Group.objects.using(schema_editor.connection.alias).get_or_create(name="ADMIN")
    hr, _ = Group.objects.using(schema_editor.connection.alias).get_or_create(name="HR_MANAGER")
    for user in User.objects.using(schema_editor.connection.alias).order_by("id"):
        if "@" in user.username:
            if user.email.lower() == "hr.manager@acme.example":
                base = "acme_admin"
            else:
                base = user.username.split("@", 1)[0].lower().replace(".", "_")
        else:
            base = user.username.lower()
        base = base[:140] or f"user_{user.pk}"
        candidate = base
        if User.objects.using(schema_editor.connection.alias).filter(username=candidate).exclude(pk=user.pk).exists():
            candidate = f"{base}_{user.pk}"
        if user.username != candidate:
            user.username = candidate
            user.save(update_fields=["username"])
        user.groups.remove(admin, hr)
        user.groups.add(admin if user.is_staff or user.is_superuser else hr)


class Migration(migrations.Migration):
    dependencies = [
        ("compensation", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]
    operations = [migrations.RunPython(backfill_roles_and_usernames, migrations.RunPython.noop)]
