from enum import Enum

class GlobalsScopes(Enum):
    PATIENT_PROFILE_READ = 'patient-profile.read'
    PATIENT_PROFILE_WRITE = 'patient-profile.write'
    STAFF_PORTAL_READ = 'staff-portal.read'
    STAFF_PORTAL_WRITE = 'staff-portal.write'
