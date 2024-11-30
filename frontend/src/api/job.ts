import { JobCreate, Job } from "../types/job";

export const jobApi = {
  create: async (job: JobCreate): Promise<Job> => {
      const response = await fetch('/api/jobs/', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify(job),
      });
      
      if (!response.ok) {
          throw new Error('Failed to create job');
      }
      
      return response.json();
  },

  get: async (id: string): Promise<Job> => {
      const response = await fetch(`/api/jobs/${id}`);
      
      if (!response.ok) {
          throw new Error('Failed to fetch job');
      }
      
      return response.json();
  },

  list: async (): Promise<Job[]> => {
      const response = await fetch('/api/jobs/');
      
      if (!response.ok) {
          throw new Error('Failed to fetch jobs');
      }
      
      return response.json();
  },

  update: async (id: string, job: JobCreate): Promise<Job> => {
      const response = await fetch(`/api/jobs/${id}`, {
          method: 'PUT',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify(job),
      });
      
      if (!response.ok) {
          throw new Error('Failed to update job');
      }
      
      return response.json();
  },

  delete: async (id: string): Promise<void> => {
      const response = await fetch(`/api/jobs/${id}`, {
          method: 'DELETE',
      });
      
      if (!response.ok) {
          throw new Error('Failed to delete job');
      }
  },
};