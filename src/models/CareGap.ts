export type CareGapCategory = 'clinical' | 'administrative' | 'behavioral' | 'external';

export type CareGapCreatedBy = 'system' | 'user';

export type CareGapSeverity = 'low' | 'medium' | 'high' | 'critical';

export type CareGapStatus = 'open' | 'investigating' | 'intervening' | 'resolved' | 'accepted_risk';

export interface CareGap {
  gapId: string;
  gapType: string;
  gapCategory: CareGapCategory;
  createdAt: string;
  createdBy: CareGapCreatedBy;
  description: string;
  severity: CareGapSeverity;
  severityRationale: string;
  status: CareGapStatus;
  outstandingItemIds: string[];
}
