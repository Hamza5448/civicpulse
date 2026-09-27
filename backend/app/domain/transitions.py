from app.db.models.complaint import ComplaintStatus

VALID_STATUS_TRANSITIONS: dict[ComplaintStatus, frozenset[ComplaintStatus]] = {
    ComplaintStatus.OPEN: frozenset({ComplaintStatus.IN_PROGRESS, ComplaintStatus.REJECTED}),
    ComplaintStatus.IN_PROGRESS: frozenset({ComplaintStatus.RESOLVED, ComplaintStatus.REJECTED}),
    ComplaintStatus.RESOLVED: frozenset(),
    ComplaintStatus.REJECTED: frozenset(),
}
