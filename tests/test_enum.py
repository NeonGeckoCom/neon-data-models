from unittest import TestCase


class TestEnumClasses(TestCase):
    def test_access_roles(self):
        from neon_data_models.enum import AccessRoles
        self.assertGreater(AccessRoles.OWNER, AccessRoles.ADMIN)
        self.assertGreater(AccessRoles.ADMIN, AccessRoles.USER)
        self.assertGreater(AccessRoles.USER, AccessRoles.GUEST)
        self.assertGreater(AccessRoles.GUEST, AccessRoles.NONE)
        self.assertFalse(AccessRoles.NONE)
