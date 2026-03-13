export type ClaimPhase = 'blind' | 'acute' | 'post-acute' | 'recovery' | 'resolution' | 'maintenance';

export interface ClaimMilestone {
  id: string;
  name: string;
  phase: ClaimPhase;
  estimatedDays: number;
  actualDays: number | null;
  variation: number;
}
