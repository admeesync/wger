class Role:
    MEMBER = 'member'
    TRAINER = 'trainer'
    GYM_ADMIN = 'gym_admin'
    SUPER_ADMIN = 'super_admin'

    ALL = (MEMBER, TRAINER, GYM_ADMIN, SUPER_ADMIN)
    STAFF = (TRAINER, GYM_ADMIN, SUPER_ADMIN)
