"""
OpenFGA Configuration for Rebecca
"""
import os

# OpenFGA connection settings
OPENFGA_API_URL = os.getenv('OPENFGA_URL', 'http://localhost:8080')
OPENFGA_STORE_ID = os.getenv('OPENFGA_STORE_ID', '01JYYK7BG878R7NVQRECYFT5C4')
OPENFGA_MODEL_ID = os.getenv('OPENFGA_MODEL_ID', '01JYYK7D1CY0KMVPJV6HVYZMEH')

# Authorization model object types
OBJECT_TYPES = {
    'USER': 'user',
    'GROUP': 'group', 
    'FOLDER': 'folder',
    'DOC': 'doc'
}

# Common relations
RELATIONS = {
    'OWNER': 'owner',
    'VIEWER': 'viewer', 
    'MEMBER': 'member',
    'CAN_READ': 'can_read',
    'CAN_WRITE': 'can_write',
    'CAN_SHARE': 'can_share'
}
