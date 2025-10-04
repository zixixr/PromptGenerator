import { create } from 'zustand'
import { Project } from '../lib/api'

interface ProjectState {
  projects: Project[]
  currentProject: Project | null
  setProjects: (projects: Project[]) => void
  setCurrentProject: (project: Project | null) => void
  addProject: (project: Project) => void
  removeProject: (projectId: string) => void
  updateProject: (projectId: string, updates: Partial<Project>) => void
}

export const useProjectStore = create<ProjectState>((set) => ({
  projects: [],
  currentProject: null,

  setProjects: (projects) => set({ projects }),

  setCurrentProject: (project) => set({ currentProject: project }),

  addProject: (project) =>
    set((state) => ({ projects: [project, ...state.projects] })),

  removeProject: (projectId) =>
    set((state) => ({
      projects: state.projects.filter((p) => p.id !== projectId),
    })),

  updateProject: (projectId, updates) =>
    set((state) => ({
      projects: state.projects.map((p) =>
        p.id === projectId ? { ...p, ...updates } : p
      ),
      currentProject:
        state.currentProject?.id === projectId
          ? { ...state.currentProject, ...updates }
          : state.currentProject,
    })),
}))
