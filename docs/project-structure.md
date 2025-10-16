# MioVo Project Structure

## Directory Layout

```
MioVo/
├── .gitignore
├── .dockerignore
├── README.md
├── CHANGELOG.md
├── package.json                 # Electron + React dependencies
├── tsconfig.json               # TypeScript configuration
├── vite.config.ts              # Vite configuration
├── tailwind.config.ts          # Tailwind CSS configuration
├── postcss.config.mjs          # PostCSS configuration
│
├── electron/                   # Electron main process
│   ├── main.ts                # Main entry point
│   ├── preload.ts             # Preload script
│   └── ipc-handlers.ts        # IPC message handlers
│
├── src/                       # React frontend
│   ├── main.tsx              # React entry point
│   ├── App.tsx               # Root component
│   ├── globals.css           # Global styles (Tailwind)
│   │
│   ├── components/           # React components
│   │   ├── layout/          # Layout components
│   │   ├── reading/         # 朗読モード components
│   │   ├── singing/         # 歌唱モード components
│   │   ├── common/          # Common UI components
│   │   └── timeline/        # Timeline editor
│   │
│   ├── hooks/               # Custom React hooks
│   ├── stores/              # State management (Zustand/Jotai)
│   ├── types/               # TypeScript type definitions
│   └── utils/               # Utility functions
│
├── backend/                  # Python backend services
│   ├── requirements.txt     # Python dependencies
│   ├── gateway/             # FastAPI Gateway (port 8000)
│   │   ├── main.py         # FastAPI app entry
│   │   ├── routers/        # API routers
│   │   ├── models/         # Data models (Pydantic)
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utility functions
│   │
│   ├── aivisspeech/        # AivisSpeech integration
│   │   ├── client.py       # API client wrapper
│   │   └── models.py       # AudioQuery models
│   │
│   └── rvc/                # RVC integration (Docker)
│       ├── Dockerfile      # RVC container
│       ├── requirements.txt
│       ├── server.py       # rvc-python API wrapper
│       └── models/         # RVC model storage
│
├── docker/                  # Docker configurations
│   ├── docker-compose.yml  # Multi-service orchestration
│   ├── rvc.Dockerfile      # RVC service (NGC base)
│   └── .env.template       # Environment variables template
│
├── scripts/                 # Utility scripts
│   ├── tri-search.mjs      # 3-stage API search
│   ├── setup-env.ps1       # Environment setup (Windows)
│   ├── setup-env.sh        # Environment setup (Linux/macOS)
│   └── download-models.py  # Model download utility
│
├── config/                  # Configuration files
│   ├── default.yml         # Default configuration
│   ├── development.yml     # Development overrides
│   └── production.yml      # Production overrides
│
├── memory-bank/            # Project memory (persistent)
│   ├── .initialized
│   ├── projectbrief.md
│   ├── productContext.md
│   ├── techContext.md
│   ├── systemPatterns.md
│   ├── activeContext.md
│   └── progress.md
│
├── docs/                   # Documentation
│   ├── sources.md         # Reference sources
│   ├── decisions.md       # Architecture decisions
│   ├── operations.md      # Operations manual
│   ├── api-reference.md   # API documentation
│   └── project-structure.md  # This file
│
├── tmp/                   # Temporary files
│   ├── cli/              # Command output logs
│   ├── research/         # Search results
│   └── cache/            # Application cache
│
├── backup/               # Backup files (auto-generated)
│   └── auto/            # Automatic backups
│
├── dist/                # Build output (gitignored)
│   ├── electron/       # Electron app
│   └── web/            # Web assets
│
└── models/             # AI models (gitignored)
    ├── aivisspeech/   # AivisSpeech models
    ├── rvc/           # RVC voice models
    └── demucs/        # Demucs separation models
```

## Key Directories

### `/electron` - Electron Main Process
- **Purpose**: Desktop app framework, window management, system integration
- **Technology**: TypeScript, Electron
- **Key Files**:
  - `main.ts`: App lifecycle, window creation
  - `preload.ts`: Bridge between main/renderer
  - `ipc-handlers.ts`: IPC communication handlers

### `/src` - React Frontend
- **Purpose**: User interface, state management
- **Technology**: React, TypeScript, Tailwind CSS, Motion
- **Key Patterns**:
  - Timeline-based editor for text
  - Real-time waveform visualization
  - Keyboard shortcuts (Space, Arrow keys)

### `/backend` - Python Services
- **Purpose**: Audio processing, API gateway
- **Technology**: Python, FastAPI, uvicorn
- **Services**:
  - **Gateway (8000)**: Job queue, progress tracking
  - **AivisSpeech**: TTS integration
  - **RVC**: Voice conversion (Dockerized)

### `/docker` - Container Configurations
- **Purpose**: Isolate PyTorch/RVC from host environment
- **Strategy**: NGC base image for RTX 5090 compatibility
- **Key Files**:
  - `docker-compose.yml`: Multi-service orchestration
  - `rvc.Dockerfile`: RVC service container

### `/config` - Application Configuration
- **Purpose**: Environment-specific settings
- **Format**: YAML
- **Hierarchy**: default → development/production

### `/memory-bank` - Project Memory
- **Purpose**: Persistent project context
- **Technology**: Markdown
- **Usage**: AI assistant memory across sessions

## File Naming Conventions

- **Components**: PascalCase (e.g., `AudioPlayer.tsx`)
- **Utilities**: camelCase (e.g., `textChunker.ts`)
- **Configs**: kebab-case (e.g., `tailwind.config.ts`)
- **Scripts**: kebab-case with extension (e.g., `setup-env.ps1`)
- **Python**: snake_case (e.g., `audio_query.py`)

## Build Artifacts (gitignored)

- `dist/`: Compiled output
- `node_modules/`: Node dependencies
- `.venv/`, `venv/`: Python virtual environments
- `models/`: Large AI models
- `tmp/`: Temporary files
- `*.log`: Log files
- `.env`: Environment variables
