/**
 * Frontend API domain types for ForensiWeb
 */

export interface Case {
  id: string;
  title: string;
  description?: string;
  status: string;
  priority: string;
  created_at: string;
  updated_at: string;
}

export interface EvidenceItem {
  id: string;
  case_id: string;
  source: string;
  filename: string;
  sha256: string;
  size_bytes: number;
  mime_type: string;
  status: "stored" | "verified" | "tampered" | "parsed";
  acquired_at: string;
}

export interface NormalizedEvent {
  event_id: string;
  case_id: string;
  timestamp: string;
  source_type: string;
  attack_stage: string;
  severity: string;
  action: string;
  actor: { ip?: string; [key: string]: any };
  target: { service_name?: string; path?: string; [key: string]: any };
  raw_content: string;
  source_location?: {
    line_number: number;
    byte_offset_start: number;
    byte_offset_end: number;
  };
  evidence_ref?: {
    artifact_name: string;
    sha256: string;
  };
}

export interface DetectionAlert {
  id: string;
  case_id: string;
  rule_id: string;
  rule_name: string;
  description: string;
  severity: string;
  attack_stage: string;
  explanation: string;
  matched_event_ids: string[];
  evidence_references: string[];
  created_at: string;
}

export interface TimelineEntry {
  id: string;
  case_id: string;
  timestamp: string;
  attack_stage: string;
  title: string;
  summary: string;
  order_index: number;
  event_ids: string[];
  detection_ids: string[];
  evidence_references: string[];
  classification: "Observed" | "Likely" | "Correlated" | "Inferred";
  confidence: number;
  metadata: Record<string, any>;
  created_at: string;
}

export interface AttackChainNode {
  id: string;
  label: string;
  stage: string;
  node_type: string;
  timestamp: string;
  classification: string;
  confidence: number;
  evidence_references: string[];
  details: Record<string, any>;
}

export interface AttackChainEdge {
  source_id: string;
  target_id: string;
  relation_type: string;
  confidence: number;
  classification: string;
  explanation: string;
}

export interface AttackChainGraph {
  case_id: string;
  nodes: AttackChainNode[];
  edges: AttackChainEdge[];
  root_causes: string[];
  terminal_impacts: string[];
  stage_sequence: string[];
  overall_confidence: number;
  reconstructed_at: string;
}

export interface Finding {
  id: string;
  case_id: string;
  title: string;
  severity: string;
  attack_stage: string;
  analysis_summary: string;
  mitigation_summary?: string;
  evidence_references: string[];
  detection_ids: string[];
  event_ids: string[];
  created_at: string;
  updated_at: string;
}

export interface TraceabilityHop {
  layer: string;
  entity_id: string;
  status: string;
  details: Record<string, any>;
}

export interface TraceabilityReport {
  finding_id: string;
  case_id: string;
  is_fully_traceable: boolean;
  chain_depth: number;
  hops: TraceabilityHop[];
  unresolved_links: string[];
  verified_sha256?: string;
  original_file_path?: string;
  verified_at: string;
}

export interface RiskFactor {
  factor: string;
  points: number;
  rationale: string;
}

export interface RiskSummary {
  case_id: string;
  risk_score: number;
  risk_level: string;
  explanation_factors: RiskFactor[];
  calculated_at: string;
}

export interface DashboardAnalytics {
  case_overview: {
    case_id: string;
    title: string;
    status: string;
    priority: string;
    created_at: string;
    updated_at: string;
  };
  evidence_metrics: {
    total_artifacts: number;
    verified_hashes: number;
    tampered_count: number;
    total_bytes: number;
    format_breakdown: Record<string, number>;
  };
  event_metrics: {
    total_events: number;
    by_source_type: Record<string, number>;
    by_attack_stage: Record<string, number>;
  };
  detection_metrics: {
    total_alerts: number;
    by_severity: Record<string, number>;
    by_rule: Record<string, number>;
  };
  finding_metrics: {
    total_findings: number;
    by_severity: Record<string, number>;
    mitigated_count: number;
    unmitigated_count: number;
  };
  event_trends: Array<{
    bucket_start: string;
    count: number;
    stages: Record<string, number>;
  }>;
  severity_distribution: {
    counts: Record<string, number>;
    percentages: Record<string, number>;
  };
  attack_stage_analytics: {
    stages_detected: string[];
    highest_stage_reached: string;
    sequence_completion_percent: number;
  };
  risk_summary: RiskSummary;
}
