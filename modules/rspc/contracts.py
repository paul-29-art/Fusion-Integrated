"""
RSPC Cross-Module Public Contract (ADR-0010, ADR-0013 compliant).
Safe for other Fusion modules to import and query.
"""
from decimal import Decimal
from typing import Optional, Dict, Any, List
from django.contrib.auth import get_user_model
from .models import ResearchProposal, ConsultancyProject, FinancialRequest

User = get_user_model()


def get_faculty_active_proposals(user_id: int) -> List[Dict[str, Any]]:
    """Return summary of active/sanctioned research proposals for a faculty member."""
    proposals = ResearchProposal.objects.filter(pi_id=user_id).values(
        'id', 'title', 'sponsor_agency', 'budget', 'sanctioned_budget', 'status', 'is_sanctioned'
    )
    return list(proposals)


def get_faculty_consultancies(user_id: int) -> List[Dict[str, Any]]:
    """Return summary of consultancy projects for a faculty member."""
    projects = ConsultancyProject.objects.filter(pi_id=user_id).values(
        'id', 'title', 'client_name', 'total_cost', 'institutional_share', 'investigator_share', 'status'
    )
    return list(projects)


def get_project_budget_status(proposal_id: int) -> Optional[Dict[str, Any]]:
    """Return sanctioned budget, current expenditure, and remaining balance."""
    try:
        p = ResearchProposal.objects.get(id=proposal_id)
        balance = p.sanctioned_budget - p.expenditure_total
        return {
            'proposal_id': p.id,
            'title': p.title,
            'sanctioned_budget': float(p.sanctioned_budget),
            'expenditure_total': float(p.expenditure_total),
            'remaining_balance': float(balance),
            'status': p.status,
        }
    except ResearchProposal.DoesNotExist:
        return None
