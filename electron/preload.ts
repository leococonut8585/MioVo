import { contextBridge, ipcRenderer } from 'electron'

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electron', {
  // App info
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  getAppPath: () => ipcRenderer.invoke('get-app-path'),
  
  // Window controls
  minimizeWindow: () => ipcRenderer.invoke('minimize-window'),
  maximizeWindow: () => ipcRenderer.invoke('maximize-window'),
  closeWindow: () => ipcRenderer.invoke('close-window'),
  
  // IPC communication
  send: (channel: string, data: unknown) => {
    const validChannels = ['toMain']
    if (validChannels.includes(channel)) {
      ipcRenderer.send(channel, data)
    }
  },
  
  receive: (channel: string, func: (...args: unknown[]) => void) => {
    const validChannels = ['fromMain']
    if (validChannels.includes(channel)) {
      ipcRenderer.on(channel, (_event, ...args) => func(...args))
    }
  }
})

// Type definitions for window.electron
declare global {
  interface Window {
    electron: {
      getAppVersion: () => Promise<string>
      getAppPath: () => Promise<string>
      minimizeWindow: () => Promise<void>
      maximizeWindow: () => Promise<void>
      closeWindow: () => Promise<void>
      send: (channel: string, data: unknown) => void
      receive: (channel: string, func: (...args: unknown[]) => void) => void
    }
  }
}
