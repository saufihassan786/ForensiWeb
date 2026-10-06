"""Initial core domain tables migration.

Revision ID: 0001_initial
Revises: None
Create Date: 2026-10-06 23:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Cases Table
    op.create_table(
        "cases",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("priority", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cases")),
    )
    op.create_index(op.f("ix_cases_priority"), "cases", ["priority"], unique=False)
    op.create_index(op.f("ix_cases_status"), "cases", ["status"], unique=False)
    op.create_index(op.f("ix_cases_title"), "cases", ["title"], unique=False)

    # 2. Evidence Table
    op.create_table(
        "evidence",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=1024), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("media_type", sa.String(length=100), nullable=False),
        sa.Column("acquired_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], name=op.f("fk_evidence_case_id_cases"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_evidence")),
    )
    op.create_index(op.f("ix_evidence_case_id"), "evidence", ["case_id"], unique=False)
    op.create_index(op.f("ix_evidence_sha256"), "evidence", ["sha256"], unique=False)
    op.create_index(op.f("ix_evidence_source"), "evidence", ["source"], unique=False)
    op.create_index(op.f("ix_evidence_status"), "evidence", ["status"], unique=False)

    # 3. Events Table
    op.create_table(
        "events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("evidence_id", sa.String(length=36), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("actor_ip", sa.String(length=64), nullable=True),
        sa.Column("target_service", sa.String(length=100), nullable=True),
        sa.Column("action_method", sa.String(length=20), nullable=True),
        sa.Column("action_path", sa.String(length=1024), nullable=True),
        sa.Column("attack_stage", sa.String(length=50), nullable=True),
        sa.Column("raw_payload", sa.Text(), nullable=True),
        sa.Column("normalized_data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], name=op.f("fk_events_case_id_cases"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["evidence_id"], ["evidence.id"], name=op.f("fk_events_evidence_id_evidence"), ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
    )
    op.create_index(op.f("ix_events_actor_ip"), "events", ["actor_ip"], unique=False)
    op.create_index(op.f("ix_events_attack_stage"), "events", ["attack_stage"], unique=False)
    op.create_index(op.f("ix_events_case_id"), "events", ["case_id"], unique=False)
    op.create_index(op.f("ix_events_event_type"), "events", ["event_type"], unique=False)
    op.create_index(op.f("ix_events_evidence_id"), "events", ["evidence_id"], unique=False)
    op.create_index(op.f("ix_events_severity"), "events", ["severity"], unique=False)
    op.create_index(op.f("ix_events_source"), "events", ["source"], unique=False)
    op.create_index(op.f("ix_events_timestamp"), "events", ["timestamp"], unique=False)

    # 4. Detections Table
    op.create_table(
        "detections",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("rule_id", sa.String(length=100), nullable=False),
        sa.Column("rule_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("attack_stage", sa.String(length=50), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("matched_event_ids", sa.JSON(), nullable=False),
        sa.Column("evidence_references", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], name=op.f("fk_detections_case_id_cases"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_detections")),
    )
    op.create_index(op.f("ix_detections_attack_stage"), "detections", ["attack_stage"], unique=False)
    op.create_index(op.f("ix_detections_case_id"), "detections", ["case_id"], unique=False)
    op.create_index(op.f("ix_detections_rule_id"), "detections", ["rule_id"], unique=False)
    op.create_index(op.f("ix_detections_severity"), "detections", ["severity"], unique=False)

    # 5. Timeline Entries Table
    op.create_table(
        "timeline_entries",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attack_stage", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("event_ids", sa.JSON(), nullable=False),
        sa.Column("evidence_references", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], name=op.f("fk_timeline_entries_case_id_cases"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_timeline_entries")),
    )
    op.create_index(op.f("ix_timeline_entries_attack_stage"), "timeline_entries", ["attack_stage"], unique=False)
    op.create_index(op.f("ix_timeline_entries_case_id"), "timeline_entries", ["case_id"], unique=False)
    op.create_index(op.f("ix_timeline_entries_order_index"), "timeline_entries", ["order_index"], unique=False)
    op.create_index(op.f("ix_timeline_entries_timestamp"), "timeline_entries", ["timestamp"], unique=False)

    # 6. Findings Table
    op.create_table(
        "findings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("attack_stage", sa.String(length=50), nullable=False),
        sa.Column("analysis_summary", sa.Text(), nullable=False),
        sa.Column("mitigation_summary", sa.Text(), nullable=True),
        sa.Column("evidence_references", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], name=op.f("fk_findings_case_id_cases"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_findings")),
    )
    op.create_index(op.f("ix_findings_attack_stage"), "findings", ["attack_stage"], unique=False)
    op.create_index(op.f("ix_findings_case_id"), "findings", ["case_id"], unique=False)
    op.create_index(op.f("ix_findings_severity"), "findings", ["severity"], unique=False)

    # 7. Reports Table
    op.create_table(
        "reports",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("report_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=1024), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("format", sa.String(length=20), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], name=op.f("fk_reports_case_id_cases"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_reports")),
    )
    op.create_index(op.f("ix_reports_case_id"), "reports", ["case_id"], unique=False)
    op.create_index(op.f("ix_reports_report_type"), "reports", ["report_type"], unique=False)
    op.create_index(op.f("ix_reports_sha256"), "reports", ["sha256"], unique=False)

    # 8. Audit Logs Table
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("actor", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("resource_id", sa.String(length=100), nullable=True),
        sa.Column("details_json", sa.JSON(), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_logs")),
    )
    op.create_index(op.f("ix_audit_logs_action"), "audit_logs", ["action"], unique=False)
    op.create_index(op.f("ix_audit_logs_resource_type"), "audit_logs", ["resource_type"], unique=False)
    op.create_index(op.f("ix_audit_logs_timestamp"), "audit_logs", ["timestamp"], unique=False)


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("reports")
    op.drop_table("findings")
    op.drop_table("timeline_entries")
    op.drop_table("detections")
    op.drop_table("events")
    op.drop_table("evidence")
    op.drop_table("cases")
