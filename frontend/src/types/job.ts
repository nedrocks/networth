export interface Job {
  id: string;      // KSUID unique identifier
  name: string;    // Human readable name
  startDate: string; // ISO 8601 date string
  endDate: string | null; // ISO 8601 date string or null
}

export interface JobCreate {
  name: string;
  startDate: string;
  endDate: string | null;
}
