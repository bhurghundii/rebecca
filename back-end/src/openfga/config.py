"""
OpenFGA Configuration for Rebecca
"""
import os

# OpenFGA connection settings
OPENFGA_API_URL = os.getenv('OPENFGA_URL', 'http://localhost:8080')
OPENFGA_STORE_ID = os.getenv('OPENFGA_STORE_ID', '01JZ0393KCZDMBMW24TMP84BCR')
OPENFGA_MODEL_ID = os.getenv('OPENFGA_MODEL_ID', '01JZ0KH75HW7DKS3QF8J17PW4P')

# Authorization model object types
OBJECT_TYPES = {
    'USER': 'user',
    'GROUP': 'group', 
    'FOLDER': 'folder',
    'DOC': 'doc',
    'DOCUMENT': 'document',
    'PROJECT': 'project'
}

# Common relations
RELATIONS = {
    'OWNER': 'owner',
    'EDITOR': 'editor',
    'VIEWER': 'viewer', 
    'MEMBER': 'member',
    'CAN_READ': 'can_read',
    'CAN_WRITE': 'can_write',
    'CAN_SHARE': 'can_share'
}
