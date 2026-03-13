import type { CareGap } from './CareGap';
import type { ClaimMilestone } from './ClaimMilestone';
import type { OutstandingItem } from './OutstandingItem';

export interface Claim {
  milestones: ClaimMilestone[];
  outstandingItems: OutstandingItem[];
  careGaps: CareGap[];
}
