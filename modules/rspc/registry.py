"""
RSPC Platform Registry & Access Control Configuration.
Synchronized with Fusion ERP Platform standards.
"""

MODULE = {
    "code": "rspc",
    "name": "Research, Sponsored Projects & Consultancy",
    "description": "Digitization and governance of sponsored research, consultancy projects, and grant lifecycles.",
    "version": "1.0.0",
}

NAV_ITEMS = [
    {
        "code": "rspc_dashboard",
        "label": "RSPC Hub",
        "path": "/rspc",
        "icon": "IconFlask",
        "roles": ["FACULTY", "HOD", "RSPC_ADMIN", "DEAN_RSPC", "DIRECTOR"],
    },
    {
        "code": "rspc_proposals",
        "label": "Research Proposals",
        "path": "/rspc/proposals",
        "icon": "IconFileCertificate",
        "roles": ["FACULTY", "HOD", "RSPC_ADMIN", "DEAN_RSPC", "DIRECTOR"],
    },
    {
        "code": "rspc_consultancy",
        "label": "Consultancy Projects",
        "path": "/rspc/consultancy",
        "icon": "IconBriefcase",
        "roles": ["FACULTY", "HOD", "RSPC_ADMIN", "DEAN_RSPC", "DIRECTOR"],
    },
    {
        "code": "rspc_staff",
        "label": "Staff Appointments",
        "path": "/rspc/staff",
        "icon": "IconUsers",
        "roles": ["FACULTY", "RSPC_ADMIN", "DEAN_RSPC", "DIRECTOR"],
    },
    {
        "code": "rspc_finance",
        "label": "Financial Management",
        "path": "/rspc/finance",
        "icon": "IconReceipt2",
        "roles": ["FACULTY", "RSPC_ADMIN", "DEAN_RSPC", "DIRECTOR"],
    },
    {
        "code": "rspc_procurement",
        "label": "Procurement Requisitions",
        "path": "/rspc/procurement",
        "icon": "IconShoppingCart",
        "roles": ["FACULTY", "RSPC_ADMIN", "DEAN_RSPC", "DIRECTOR"],
    },
    {
        "code": "rspc_reports_closure",
        "label": "Reports & Closure",
        "path": "/rspc/reports-closure",
        "icon": "IconArchive",
        "roles": ["FACULTY", "RSPC_ADMIN", "DEAN_RSPC", "DIRECTOR"],
    },
    {
        "code": "rspc_audit",
        "label": "Audit Logs",
        "path": "/rspc/audit",
        "icon": "IconHistory",
        "roles": ["RSPC_ADMIN", "DEAN_RSPC", "DIRECTOR"],
    },
]

PERMISSIONS = [
    ("can_submit_proposal", "Can submit research proposals"),
    ("can_recommend_proposal", "Can recommend research proposals at department level"),
    ("can_verify_rspc_records", "Can verify RSPC records for completeness and compliance"),
    ("can_approve_within_delegated_powers", "Can approve eligible RSPC requests within delegated authority"),
    ("can_authorize_high_value", "Can authorize high-value and strategic RSPC requests"),
]

ROLE_GRANTS = {
    "FACULTY": ["can_submit_proposal"],
    "HOD": ["can_submit_proposal", "can_recommend_proposal"],
    "RSPC_ADMIN": ["can_verify_rspc_records"],
    "DEAN_RSPC": ["can_approve_within_delegated_powers", "can_verify_rspc_records"],
    "DIRECTOR": ["can_authorize_high_value", "can_approve_within_delegated_powers"],
}
