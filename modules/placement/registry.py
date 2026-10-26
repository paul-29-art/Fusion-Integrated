"""What the server tells the shell about this module (ADR-0010).

Nav items carry `required_permission` and the server filters before sending.
"""
MODULE = {
    "code": "placement",
    "label": "Leave Management",
    "icon": "FaCalendarAlt",
    "base_path": "/elm/apply",
    "nav_section": "Employee Services",
    "sort_order": 10,
    "status": "active",
}

NAV_ITEMS = [
    {
        "code": "elm.apply",
        "label": "Apply for Leave",
        "icon": "FaClipboardList",
        "to": "/elm/apply",
        "required_permission": "",
        "sort_order": 10,
    },
    {
        "code": "elm.balance",
        "label": "Leave Balance & History",
        "icon": "FaClipboardCheck",
        "to": "/elm/balance",
        "required_permission": "",
        "sort_order": 20,
    },
    {
        "code": "elm.approver",
        "label": "Approver Action Portal",
        "icon": "FaUserCheck",
        "to": "/elm/approver",
        "required_permission": "",
        "sort_order": 30,
    },
]

PERMISSIONS = [
    ("elm.apply", "Apply for employee leave"),
    ("elm.approve", "Approve employee leave applications"),
]

SYSTEM_PERMISSIONS = []

ROLE_GRANTS = {
    "student": ["elm.apply"],
    "faculty": ["elm.apply", "elm.approve"],
    "admin": ["elm.apply", "elm.approve"],
}
