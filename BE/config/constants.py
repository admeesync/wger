class Role:
    MEMBER = 'member'
    TRAINER = 'trainer'
    GYM_ADMIN = 'gym_admin'
    SUPER_ADMIN = 'super_admin'

    ALL = (MEMBER, TRAINER, GYM_ADMIN, SUPER_ADMIN)
    STAFF = (TRAINER, GYM_ADMIN, SUPER_ADMIN)


class MemberType:
    """Tags on a `members` row — tracking only, none of these get login access
    (that stays exclusive to the gym_admin account created at registration)."""
    MEMBER = 'member'
    TRAINER = 'trainer'
    OWNER = 'owner'
    STAFF = 'staff'

    ALL = (MEMBER, TRAINER, OWNER, STAFF)


class InquiryTag:
    HOT = 'hot'
    COOL = 'cool'
    NORMAL = 'normal'

    ALL = (HOT, COOL, NORMAL)
