import { app, BrowserWindow, ipcMain } from 'electron'
import path from 'path'

// Environment check
const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged

// Main window reference
let mainWindow: BrowserWindow | null = null

// Create main window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 1024,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    },
    title: 'MioVo - Local Voice Studio',
    titleBarStyle: 'default',
    show: false, // Show after ready-to-show
    backgroundColor: '#1e293b'
  })

  // Load app
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../web/index.html'))
  }

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow?.show()
  })

  // Handle window close
  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// App lifecycle events
app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// IPC handlers
ipcMain.handle('get-app-version', () => {
  return app.getVersion()
})

ipcMain.handle('get-app-path', () => {
  return app.getAppPath()
})

ipcMain.handle('minimize-window', () => {
  mainWindow?.minimize()
})

ipcMain.handle('maximize-window', () => {
  if (mainWindow?.isMaximized()) {
    mainWindow.unmaximize()
  } else {
    mainWindow?.maximize()
  }
})

ipcMain.handle('close-window', () => {
  mainWindow?.close()
})

// Error handling
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error)
})

process.on('unhandledRejection', (reason) => {
  console.error('Unhandled Rejection:', reason)
})
