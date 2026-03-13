export type OutstandingItemCategory = 'IW' | 'Employer' | 'Provider' | 'Internal' | 'External';

export type OutstandingItemStatus = 'open' | 'completed' | 'cancelled';

export type UrgencyType = 'milestone-protecting' | 'deadline-driven' | 'discretionary';

export interface OutstandingItem {
  id: string;
  owner: string;
  category: OutstandingItemCategory;
  description: string;
  createdAt: string;
  status: OutstandingItemStatus;
  urgencyType: UrgencyType;
  terminalAt: string | null;
}
