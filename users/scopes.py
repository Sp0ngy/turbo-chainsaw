from enum import Enum


class GlobalsScopes(Enum):
    PATIENT_PROFILE_READ = 'patient-profile.read'
    PATIENT_PROFILE_WRITE = 'patient-profile.write'
    STAFF_PORTAL_READ = 'staff-portal.read'
    STAFF_PORTAL_WRITE = 'staff-portal.write'


class ConsentScopes(Enum):
    TOS_ACCEPTED_V1_0 = 'tos-accepted-v1.0'
    MARKETING_ACCEPTED_V1_0 = 'marketing-accepted-v1.0'