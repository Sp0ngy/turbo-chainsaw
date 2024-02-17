from enum import Enum
"""
GLOBAL PERMISSIONS MODEL

This module defines the GLOBAL permissions used across the application, inspired by the Linux permission system.
Each permission is structured as 'domain.operation.permissions', where 'permissions' are defined as follows:

- r (read): Grants the ability to read or view the specified resource. Essential for operations that involve retrieving and displaying data.
- w (write): Allows for the modification or updating of the resource. This permission is necessary for any operation that changes data.
- x (execute): Permits the execution of a resource, which is applicable to scripts, programs, or any operation that involves running or processing tasks.

Additional permissions tailored to application-specific needs include:

- d (delete): Enables the removal of the resource. Critical for operations that involve the deletion of data or files.
- c (create): Grants the ability to create new instances of a resource. Important for functionalities that involve adding new data or files.
- s (share): Allows for sharing the resource with other users or systems. This permission is relevant for functionalities that involve exporting, sending, or otherwise making the resource available externally.
- a (admin): Provides administrative rights over the resource, such as setting permissions, managing access controls, or performing any high-level administrative tasks.

Each permission should be granted carefully, considering the principle of least privilege to enhance security and data protection.
"""


class GlobalPermissions(Enum):
    EHR_PSEUDO_RWX = 'ehr.pseudo.rwx'
    EHR_PSEUDO_R = 'ehr.pseudo.r'
    USERS_NAME_R = 'users.name.r'

def is_valid_permission(permission):
    if permission in GlobalPermissions:
        return True
    else:
        return False