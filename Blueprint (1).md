APP NAME: Speecher

🎯 SPEECHER - PRODUCTION-GRADE BLUEPRINT
EXECUTIVE SUMMARY
Speecher is a production-ready AI-powered Text-to-Speech Creator Platform designed for three distinct user segments: casual users seeking quick voice conversions, content creators requiring advanced editing capabilities, and professional voice users demanding studio-grade control. This blueprint follows enterprise architecture patterns, ensuring scalability, maintainability, and monetization readiness from day one.

1. ARCHITECTURE OVERVIEW
1.1 System Architecture
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                              │
│  Next.js 15 (App Router) + React 19 - Vercel Deployment    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Quick Jobs   │  │  Dashboard   │  │Creator Studio│     │
│  │ (No Auth)    │  │ (Authenticated│  │(Authenticated│     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                          │
                    HTTPS/REST API
                          │
┌─────────────────────────────────────────────────────────────┐
│              SUPABASE (Backend Services)                     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Auth       │  │  PostgreSQL  │  │   Storage    │     │
│  │  (Row Level  │  │  (Database)  │  │  (R2/S3)     │     │
│  │  Security)   │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │  Realtime    │  │  Edge Funcs  │                        │
│  │  (Webhooks)  │  │  (Triggers)  │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                          │
                 Async Job Queue (HTTP/Webhooks)
                          │
┌─────────────────────────────────────────────────────────────┐
│          PYTHON AI SERVICE (Hostinger VPS)                   │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │           Job Queue Worker (Celery)              │      │
│  └──────────────────────────────────────────────────┘      │
│                          │                                   │
│  ┌────────────────┬──────────────┬─────────────────┐       │
│  │  TTS Engine    │ Voice Clone  │  Audio Process  │       │
│  │  (Coqui/Bark)  │ (RVC/So-VITS)│  (FFmpeg/Sox)   │       │
│  └────────────────┴──────────────┴─────────────────┘       │
│                                                              │
│  ┌────────────────┬──────────────┬─────────────────┐       │
│  │  Translation   │ Video Prompt │  Voice Memory   │       │
│  │  (Whisper)     │ Generation   │  (Embeddings)   │       │
│  └────────────────┴──────────────┴─────────────────┘       │
│                                                              │
│  ┌─────────────────────────────────────────────────┐       │
│  │         Docker Containers (Scalable)            │       │
│  │  - Worker Nodes (Auto-scale based on queue)     │       │
│  │  - Redis (Job Queue)                            │       │
│  │  - Model Cache (Optimized Loading)              │       │
│  └─────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
1.2 Data Flow Patterns
Synchronous Operations (Next.js → Supabase):

User authentication
Profile management
Project CRUD operations
Usage statistics retrieval
Payment processing

Asynchronous Operations (Next.js → Python Service → Supabase):

User initiates AI job (TTS, voice cloning, etc.)
Next.js creates job record in Supabase with status: pending
Python service polls/receives webhook from Supabase
Python service processes job, updates status in real-time
Completed audio stored in Supabase Storage
Job record updated with result URLs and metadata
Next.js receives real-time update via Supabase Realtime
UI updates automatically


2. APPLICATION STRUCTURE
2.1 Quick Jobs (No Authentication Required)
Purpose: Convert first-time visitors into users through instant value demonstration while preventing abuse.
2.1.1 Access Control Mechanism
Multi-Layer Fingerprinting:
typescript// Tracking Strategy
interface QuickJobFingerprint {
  cookieId: string;           // Browser cookie (primary)
  localStorageId: string;     // Persistent storage
  sessionId: string;          // Session-based
  browserFingerprint: {       // Lightweight fingerprinting
    userAgent: string;
    screenResolution: string;
    timezone: number;
    language: string;
    canvasFingerprint: string; // Non-invasive canvas hash
  };
  ipAddress: string;          // Backend validation
  timestamp: Date;
}
Detection Logic:

Cookie check (client-side, instant)
LocalStorage verification (client-side, instant)
Canvas fingerprint (client-side, 50ms)
IP + User-Agent combo (backend, 100ms)
If ANY match found → Block and show upgrade prompt
If NO match → Allow ONE job, create all tracking markers

Abuse Prevention:

Rate limit: 1 request per 5 minutes per IP
Max file size: 5MB for audio, 1000 characters for text
Request validation via Supabase Edge Functions
Automatic IP blocking after 3 failed attempts

2.1.2 Available Quick Jobs
1. Text-to-Speech (Basic)
typescriptinterface QuickTTSJob {
  input: {
    text: string;              // Max 1000 chars
    language: LanguageCode;    // Auto-detected or selected
    voicePreset: 'male' | 'female' | 'neutral'; // Limited options
  };
  output: {
    audioUrl: string;          // 24-hour expiry
    watermark: boolean;        // Always true
    format: 'mp3';            // Fixed format
    duration: number;          // In seconds
  };
  restrictions: {
    maxDuration: 60;           // 1 minute max
    noDownload: false;         // Can play, must register to download
    expiryHours: 24;
  };
}
2. Audio-to-Speech (Transcription)
typescriptinterface QuickTranscriptionJob {
  input: {
    audioFile: File;           // Max 5MB, 60 seconds
    sourceLanguage?: LanguageCode; // Auto-detect if empty
  };
  output: {
    transcript: string;
    confidence: number;
    detectedLanguage: LanguageCode;
    timestamps: Array<{word: string; start: number; end: number}>;
  };
  restrictions: {
    maxFileSize: 5 * 1024 * 1024; // 5MB
    maxDuration: 60;
    watermark: true;
  };
}
3. Speech Translation
typescriptinterface QuickTranslationJob {
  input: {
    audioFile: File;           // Max 5MB
    targetLanguage: LanguageCode;
    sourceLanguage?: LanguageCode; // Auto-detect
  };
  output: {
    originalTranscript: string;
    translatedText: string;
    translatedAudioUrl: string; // With watermark
  };
  restrictions: {
    maxFileSize: 5 * 1024 * 1024;
    maxDuration: 60;
    watermark: true;
    supportedLanguages: ['en', 'es', 'fr', 'de', 'pt', 'zh', 'ja', 'ko']; // Limited
  };
}
```

#### 2.1.3 Post-Job UX Flow
```
User Completes Quick Job
         ↓
[Success Screen with Preview]
         ↓
    Two Buttons:
    ┌─────────────────────────────┐
    │ Download / Save             │ → Requires Sign Up
    │ (Disabled, Upgrade Prompt)  │
    └─────────────────────────────┘
    ┌─────────────────────────────┐
    │ Create Another              │ → Blocked, Show Benefits
    │ (Show Feature Comparison)   │
    └─────────────────────────────┘
         ↓
[Modal: "Unlock Full Power"]
- Remove watermarks
- Longer durations
- Save projects
- Access Creator Studio
- Advanced voices
[Sign Up Free] [View Plans]
```

**Messaging Strategy:**
- Emphasize what they GAINED (successful conversion)
- Show what they're MISSING (Studio features, quality)
- Minimal friction signup (email + password, OAuth options)
- Onboarding: "You've already experienced Speecher. Now unlock everything."

---

### 2.2 Main Dashboard (Authenticated Users)

**Purpose:** Fast, friendly interface for quick speech generation without complexity.

#### 2.2.1 Dashboard Layout
```
┌─────────────────────────────────────────────────────────┐
│  Header: Logo | Usage (50/1000) | Plan | Avatar         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌───────────────────────────────────────────────┐     │
│  │   Quick Generate Panel                        │     │
│  │                                                │     │
│  │   [ Text Input Area - Large ]                 │     │
│  │                                                │     │
│  │   Language: [Dropdown]  Voice: [Dropdown]     │     │
│  │   Emotion: [Happy|Neutral|Sad|Excited]        │     │
│  │   Speed: [Slider 0.5x - 2x]                   │     │
│  │                                                │     │
│  │   [Generate Speech] [Save to Project]         │     │
│  └───────────────────────────────────────────────┘     │
│                                                          │
│  ┌───────────────────────────────────────────────┐     │
│  │   Recent Outputs (Last 10)                    │     │
│  │   ┌─────┐ ┌─────┐ ┌─────┐                    │     │
│  │   │Card │ │Card │ │Card │ ...                │     │
│  │   │▶ 🔽│ │▶ 🔽│ │▶ 🔽│                    │     │
│  │   └─────┘ └─────┘ └─────┘                    │     │
│  └───────────────────────────────────────────────┘     │
│                                                          │
│  ┌───────────────────────────────────────────────┐     │
│  │   Usage Stats (Read-Only)                     │     │
│  │   ━━━━━━━━━━━━━━━━━━━━━  50/1000 minutes    │     │
│  │   Projects: 5 | Voices: 2 | Storage: 150MB   │     │
│  └───────────────────────────────────────────────┘     │
│                                                          │
│  ┌───────────────────────────────────────────────┐     │
│  │   Upgrade Prompts (Contextual)                │     │
│  │   "Need longer outputs? Try Creator Pro"      │     │
│  │   "Remove watermarks with Creator Lite"       │     │
│  └───────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

#### 2.2.2 Dashboard Features

**Core Capabilities:**
1. **Text-to-Speech Generation**
   - Input: 5000 characters max (Free: 1000)
   - Voice selection: 10 preset voices (plan-dependent)
   - Emotion presets: 4 basic emotions
   - Speed control: 0.5x to 2x
   - Output: MP3, watermarked for Free tier

2. **Recent Outputs Management**
   - Last 10 generations displayed
   - In-browser playback
   - Quick download
   - "Save to Project" (redirects to Studio for paid plans)
   - Auto-delete after 30 days (Free) / 90 days (Paid)

3. **Usage Tracking (Read-Only)**
   - Minutes generated this month
   - Projects created
   - Voice clones available
   - Storage used
   - Resets monthly

4. **Contextual Upgrade Prompts**
   - Show when hitting limits
   - Display missing features in action
   - Soft nudges, not aggressive modals
   - "See what you're missing" approach

**Navigation:**
- Dashboard (current page)
- My Projects → (Paid plans only, redirects to Studio)
- Creator Studio → (Paid plans only, with feature preview for Free)
- Settings
- Billing

---

### 2.3 Creator Studio (Advanced Workspace)

**Purpose:** Professional-grade speech creation environment with timeline editing, advanced controls, and asset management.

#### 2.3.1 Studio Architecture
```
┌─────────────────────────────────────────────────────────────┐
│  Header: Project Name [Edit] | Auto-save ✓ | Export ▼       │
├─────────────────────────────────────────────────────────────┤
│  Left Sidebar: Assets                     Right Sidebar:     │
│  ┌────────────────┐                       ┌────────────┐    │
│  │ 📁 Audio       │                       │ Properties │    │
│  │ 🖼️ Images      │                       │            │    │
│  │ 🎬 Videos      │                       │ Selected:  │    │
│  │ 🎙️ Voices      │                       │ Block #3   │    │
│  │ + Upload       │                       │            │    │
│  └────────────────┘                       │ Voice: ▼   │    │
│                                            │ Emotion: ▼ │    │
│  Main Canvas Area:                        │ Speed: ━━  │    │
│  ┌─────────────────────────────────────┐  │ Pause: +   │    │
│  │  Timeline Editor                    │  │            │    │
│  │                                      │  │ [Preview]  │    │
│  │  ┌───┐ ┌───────┐ ┌───┐ ┌──────┐   │  │ [Regen]    │    │
│  │  │ 1 │ │   2   │ │ 3 │ │  4   │   │  └────────────┘    │
│  │  └───┘ └───────┘ └───┘ └──────┘   │                     │
│  │  [Scene] [Image] [Video] [Audio]  │                     │
│  │                                      │                     │
│  │  Narration: "Welcome to..."         │                     │
│  │  Duration: 0:45 / Total: 3:20      │                     │
│  └─────────────────────────────────────┘                     │
│                                                               │
│  Bottom Controls:                                            │
│  [◀◀] [▶️] [⏸️] [▶▶] ━━━━━●━━━━━━ 1:32 / 3:20            │
│  [Add Block] [Split] [Delete] [AI Assist]                   │
└─────────────────────────────────────────────────────────────┘
2.3.2 Core Studio Features
1. Timeline Block Editor
typescriptinterface NarrationBlock {
  id: string;
  type: 'narration' | 'pause' | 'music' | 'sfx';
  order: number;
  content: {
    text?: string;               // For narration blocks
    ssml?: string;              // Advanced: SSML markup
    duration?: number;          // For pauses/music
  };
  voice: {
    voiceId: string;
    voiceType: 'preset' | 'cloned' | 'custom';
    emotion: EmotionPreset;
    speed: number;              // 0.5 - 2.0
    pitch: number;              // -10 to +10
    volume: number;             // 0 - 100
  };
  assets: {
    imageId?: string;           // Linked image
    videoId?: string;           // Linked video
    backgroundMusicId?: string;
  };
  metadata: {
    generatedAudioUrl?: string;
    waveformData?: number[];    // For visualization
    duration: number;
    lastModified: Date;
    regenerationCount: number;
  };
  locked: boolean;              // Prevent accidental changes
}
Block Operations:

Add: Insert new narration/pause block at any position
Split: Divide block at cursor position (maintains voice settings)
Merge: Combine adjacent blocks (prompts for voice selection)
Reorder: Drag-and-drop timeline blocks
Regenerate: Re-process single block without affecting others
Lock/Unlock: Protect finalized blocks from changes
Copy Settings: Apply voice/emotion settings to multiple blocks

Timeline Interactions:

Visual waveform display for each block
Zoom controls (10s - 60s - 5min views)
Playback cursor with scrubbing
Block selection with multi-select (Shift/Ctrl)
Keyboard shortcuts (Space: play/pause, Delete: remove block, Ctrl+D: duplicate)

2. Advanced Speech-Optimized Text Editor
typescriptinterface SSMLTag {
  pause: '<pause duration="500ms"/>';
  emphasis: '<emphasis level="strong|moderate|reduced">';
  phoneme: '<phoneme alphabet="ipa" ph="təˈmeɪtoʊ">tomato</phoneme>';
  sayAs: '<say-as interpret-as="date|time|number|ordinal|cardinal">';
  prosody: '<prosody rate="slow|medium|fast" pitch="low|medium|high">';
  break: '<break time="200ms" strength="weak|medium|strong"/>';
}

interface PronunciationMemory {
  userId: string;
  word: string;
  ipa: string;                  // International Phonetic Alphabet
  customSpelling?: string;      // User-defined respelling
  context?: string;             // "medical term", "brand name"
  audioExample?: string;        // User can upload correct pronunciation
  appliedToProjects: string[];  // Track usage
  createdAt: Date;
}
Editor Features:

Real-time SSML preview: Syntax highlighting for tags
Intelligent suggestions: Context-aware pause/emphasis recommendations
Pronunciation dictionary:

Right-click word → Add pronunciation
Auto-apply across all blocks in project
Export/import pronunciation library
Shared pronunciations across projects (per user)


Reading time estimation: Based on speed settings
Readability score: Flesch-Kincaid grade level
Character count: Per block and total project

3. Narration-to-Video Intelligence (Studio Exclusive)
typescriptinterface NarrationToVideoInput {
  script?: string;              // Option 1: Provide full script
  videoIdea?: {                 // Option 2: Describe concept
    topic: string;
    targetAudience: string;
    tone: string;
    duration: number;           // Desired length in minutes
  };
  style: {
    narratorVoice: string;
    pacing: 'fast' | 'medium' | 'slow';
    visualStyle: string;        // "documentary", "explainer", "tutorial"
  };
}

interface NarrationToVideoOutput {
  scenes: Array<{
    sceneNumber: number;
    narrationText: string;
    duration: number;
    visualDescription: string;
    imagePrompt: string;        // DALL-E/Midjourney ready
    videoPrompt: string;        // Runway/Pika ready
    sceneType: 'intro' | 'content' | 'transition' | 'outro';
    suggestedMusic?: string;
    notes: string;
  }>;
  metadata: {
    totalDuration: number;
    sceneCount: number;
    keyThemes: string[];
    suggestedThumbnails: string[];
  };
}
AI Generation Process:

User provides script OR video idea
AI analyzes and structures content
Generates scene breakdown with timing
Creates optimized narration text per scene
Produces image prompts (specific, detailed, style-consistent)
Generates video prompts (motion description, camera angles)
Suggests background music and transitions
Output imported directly into Studio timeline

User Controls:

Edit any scene individually
Regenerate specific scenes
Adjust scene duration (AI rebalances narration)
Export prompts as CSV/JSON
One-click send to image/video services

4. Asset Integration System
typescriptinterface Asset {
  id: string;
  userId: string;
  type: 'image' | 'video' | 'audio' | 'music';
  filename: string;
  storageUrl: string;
  metadata: {
    duration?: number;          // For video/audio
    resolution?: {width: number; height: number};
    fileSize: number;
    format: string;
    uploadedAt: Date;
  };
  linkedBlocks: string[];       // Which timeline blocks use this
  tags: string[];
  aiGenerated: boolean;
}
Asset Features:

Upload: Drag-and-drop or file picker
Library view: Grid/list with thumbnails
Search/filter: By type, tags, date
Direct link: Drag asset onto timeline block
Sync editing:

Change image → All linked blocks update
Replace video → Preview updates in real-time
Swap audio → Maintains timing sync


AI integration:

Generate images from text prompts
Upscale images
Extend video clips
Background removal




3. AI FEATURES & EXECUTION MODEL
3.1 Asynchronous Job Architecture
All AI processing occurs on the Python service running on Hostinger VPS. The system uses a robust job queue pattern.
3.1.1 Job Queue System
python# Python Service Architecture

from celery import Celery
from redis import Redis
import supabase

# Initialize services
celery_app = Celery('speecher', broker='redis://localhost:6379/0')
redis_client = Redis(host='localhost', port=6379, db=0)
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

class JobType(Enum):
    TEXT_TO_SPEECH = 'text_to_speech'
    VOICE_CLONE = 'voice_clone'
    SPEECH_TRANSLATION = 'speech_translation'
    AUDIO_ENHANCEMENT = 'audio_enhancement'
    VOICE_STYLE_TRANSFER = 'voice_style_transfer'
    NARRATION_TO_VIDEO = 'narration_to_video'
    SCRIPT_TO_PERFORMANCE = 'script_to_performance'

class Job:
    def __init__(self, job_id: str, job_type: JobType, user_id: str, input_data: dict):
        self.job_id = job_id
        self.job_type = job_type
        self.user_id = user_id
        self.input_data = input_data
        self.status = 'pending'  # pending, processing, completed, failed
        self.progress = 0
        self.result = None
        self.error = None
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.retry_count = 0
        self.priority = self._calculate_priority()
    
    def _calculate_priority(self):
        # Pro users get higher priority
        user_tier = supabase_client.table('profiles').select('plan_tier').eq('id', self.user_id).single()
        if user_tier['plan_tier'] == 'creator_pro':
            return 1  # High priority
        elif user_tier['plan_tier'] == 'creator_lite':
            return 2  # Medium priority
        return 3  # Low priority
3.1.2 Job Status Tracking
typescript// Next.js - Real-time status updates

interface Job {
  id: string;
  userId: string;
  type: JobType;
  status: 'pending' | 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number;             // 0-100
  progressMessage?: string;     // "Loading model...", "Generating audio..."
  input: {
    /* job-specific input */
  };
  result?: {
    audioUrl?: string;
    metadata?: any;
  };
  error?: {
    code: string;
    message: string;
    retryable: boolean;
  };
  queuePosition?: number;       // Show user their place in queue
  estimatedTime?: number;       // Seconds until completion
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  expiresAt: Date;              // Result expiry
}

// Real-time subscription
const subscription = supabase
  .channel('job_updates')
  .on('postgres_changes', 
    { 
      event: 'UPDATE', 
      schema: 'public', 
      table: 'jobs',
      filter: `user_id=eq.${userId}`
    }, 
    (payload) => {
      updateJobStatus(payload.new);
    }
  )
  .subscribe();
3.1.3 Failure Recovery & Retry Logic
python@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_job(self, job_id: str):
    try:
        job = get_job_from_db(job_id)
        update_job_status(job_id, 'processing', progress=0)
        
        # Execute job based on type
        if job.type == JobType.TEXT_TO_SPEECH:
            result = execute_tts(job.input_data, job_id)
        elif job.type == JobType.VOICE_CLONE:
            result = execute_voice_clone(job.input_data, job_id)
        # ... other job types
        
        # Upload result to Supabase Storage
        storage_url = upload_to_storage(result.audio_data, job.user_id, job_id)
        
        # Update database
        update_job_status(
            job_id, 
            'completed', 
            progress=100,
            result={'audioUrl': storage_url, 'metadata': result.metadata}
        )
        
        # Send webhook notification (optional)
        send_completion_webhook(job.user_id, job_id, storage_url)
        
    except ModelLoadError as e:
        # Critical error, don't retry
        update_job_status(job_id, 'failed', error={'code': 'MODEL_ERROR', 'message': str(e), 'retryable': False})
        raise
    except (NetworkError, StorageError) as e:
        # Retryable error
        if self.request.retries < self.max_retries:
            update_job_status(job_id, 'pending', progress=0, error={'code': 'TEMPORARY_ERROR', 'message': str(e), 'retryable': True})
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
        else:
            update_job_status(job_id, 'failed', error={'code': 'MAX_RETRIES_EXCEEDED', 'message': str(e), 'retryable': False})
    except Exception as e:
        # Unknown error, log and mark failed
        log_error(job_id, e)
        update_job_status(job_id, 'failed', error={'code': 'UNKNOWN_ERROR', 'message': str(e), 'retryable': False})

3.2 AI Feature Specifications
3.2.1 Text-to-Speech (Core Feature)
Technology Stack:

Primary: Coqui TTS (open source, customizable)
Fallback: Bark (multilingual, emotion-aware)
Commercial (optional): ElevenLabs API (Premium voices for Pro plan)

Implementation:
pythondef execute_tts(input_data: dict, job_id: str) -> TTSResult:
    text = input_data['text']
    voice_id = input_data['voice_id']
    emotion = input_data.get('emotion', 'neutral')
    speed = input_data.get('speed', 1.0)
    pitch = input_data.get('pitch', 0)
    ssml_enabled = input_data.get('ssml', False)
    
    # Progress: 10%
    update_job_progress(job_id, 10, "Loading voice model...")
    
    # Load voice model (cached for performance)
    voice_model = load_voice_model(voice_id)
    
    # Progress: 30%
    update_job_progress(job_id, 30, "Processing text...")
    
    # Parse SSML if enabled
    if ssml_enabled:
        text_segments = parse_ssml(text)
    else:
        text_segments = [{'text': text, 'settings': {}}]
    
    # Generate audio segments
    audio_segments = []
    for i, segment in enumerate(text_segments):
        progress = 30 + (50 * (i / len(text_segments)))
        update_job_progress(job_id, progress, f"Generating audio segment {i+1}/{len(text_segments)}...")
        
        audio = voice_model.synthesize(
            text=segment['text'],
            emotion=emotion,
            speed=speed * segment.get('settings', {}).get('rate', 1.0),
            pitch=pitch + segment.get('settings', {}).get('pitch', 0)
        )
        audio_segments.append(audio)
    
    # Progress: 80%
    update_job_progress(job_id, 80, "Combining audio...")
    
    # Combine segments
    final_audio = combine_audio_segments(audio_segments)
    
    # Apply effects (normalization, compression)
    final_audio = apply_audio_processing(final_audio)
    
    # Progress: 95%
    update_job_progress(job_id, 95, "Finalizing...")
    
    # Export to file
    audio_file = export_audio(final_audio, format='mp3', bitrate=192)
    
    return TTSResult(
        audio_data=audio_file,
        metadata={
            'duration': len(final_audio) / sample_rate,
            'voice_id': voice_id,
            'emotion': emotion,
            'word_count': len(text.split()),
            'segments': len(audio_segments)
        }
    )
3.2.2 Voice Cloning (Pro Feature)
Consent & Legal:

Explicit checkbox: "I have permission to clone this voice"
Voice sample storage includes consent timestamp
User can revoke and delete cloned voices
Admin monitoring for abuse

Implementation:
pythondef execute_voice_clone(input_data: dict, job_id: str) -> VoiceCloneResult:
    user_id = input_data['user_id']
    audio_samples = input_data['audio_samples']  # List of audio file URLs
    voice_name = input_data['voice_name']
    consent_granted = input_data['consent_granted']
    
    if not consent_granted:
        raise ValueError("Voice cloning requires explicit consent")
    
    # Progress: 10%
    update_job_progress(job_id, 10, "Downloading audio samples...")
    
    # Download and validate audio samples
    audio_files = []
    for i, url in enumerate(audio_samples):
        audio = download_audio(url)
        if validate_audio_for_cloning(audio):
            audio_files.append(audio)
        else:
            raise ValueError(f"Audio sample {i+1} is not suitable for voice cloning")
    
    # Minimum 5 minutes of clean audio required
    total_duration = sum(len(a) / sample_rate for a in audio_files)
    if total_duration < 300:  # 5 minutes
        raise ValueError("At least 5 minutes of audio required for voice cloning")
    
    # Progress: 30%
    update_job_progress(job_id, 30, "Analyzing voice characteristics...")
    
    # Extract voice features using RVC or So-VITS
    voice_features = extract_voice_features(audio_files)
    
    # Progress: 60%
    update_job_progress(job_id, 60, "Training voice model...")
    
    # Fine-tune model (can take 10-30 minutes)
    voice_model = train_voice_model(voice_features, progress_callback=lambda p: update_job_progress(job_id, 60 + (p * 0.3), "Training voice model..."))
    
    # Progress: 90%
    update_job_progress(job_id, 90, "Saving voice profile...")
    
    # Save model and create voice profile
    model_path = save_voice_model(voice_model, user_id, voice_name)
    
    # Store voice profile in database
    voice_profile_id = create_voice_profile(
        user_id=user_id,
        name=voice_name,
        model_path=model_path,
        sample_audio_urls=audio_samples,
        metadata=voice_features.metadata,
        consent_timestamp=datetime.utcnow()
    )
    
    # Generate sample output for preview
    sample_text = "This is a preview of your cloned voice. How does it sound?"
    sample_audio = voice_model.synthesize(sample_text)
    sample_url = upload_to_storage(sample_audio, user_id, f"voice_sample_{voice_profile_id}")
    
    return VoiceCloneResult(
        voice_profile_id=voice_profile_id,
        sample_audio_url=sample_url,
        metadata={
            'training_duration': total_duration,
            'voice_characteristics': voice_features.characteristics,
            'quality_score': voice_features.quality_score
        }
    )
3.2.3 Narration-to-Video Intelligence (Studio Feature)
pythondef execute_narration_to_video(input_data: dict, job_id: str) -> NarrationVideoResult:
    script = input_data.get('script')
    video_idea = input_data.get('video_idea')
    style = input_data['style']
    
    # Progress: 10%
    update_job_progress(job_id, 10, "Analyzing content...")
    
    # If video idea provided, generate script first
    if video_idea and not script:
        script = generate_script_from_idea(video_idea, style)
    
    # Progress: 30%
    update_job_progress(job_id, 30, "Breaking down into scenes...")
    
    # Analyze script and break into scenes
    scenes = analyze_script_structure(script, style)
    
    # Progress: 50%
    update_job_progress(job_id, 50, "Generating visual prompts...")
    
    # Generate image and video prompts for each scene
    for i, scene in enumerate(scenes):
        progress = 50 + (40 * (i / len(scenes)))
        update_job_progress(job_id, progress, f"Processing scene {i+1}/{len(scenes)}...")
        
        # Generate image prompt (optimized for DALL-E/Midjourney)
        scene['image_prompt'] = generate_image_prompt(
            scene_description=scene['description'],
            visual_style=style['visual_style'],
            previous_prompts=[s.get('image_prompt') for s in scenes[:i]]  # Maintain consistency
        )
        
        # Generate video prompt (optimized for Runway/Pika)
        scene['video_prompt'] = generate_video_prompt(
            scene_description=scene['description'],
            narration_text=scene['narration'],
            duration=scene['duration'],
            style=style
        )
        
        # Suggest background music
        scene['suggested_music'] = suggest_music_for_scene(
            scene_mood=scene['mood'],
            duration=scene['duration']
        )
    
    # Progress: 90%
    update_job_progress(job_id, 90, "Finalizing...")
    
    # Create metadata
    metadata = {
        'total_duration': sum(s['duration'] for s in scenes),
        'scene_count': len(scenes),
        'key_themes': extract_themes(script),
        'suggested_thumbnails': generate_thumbnail_prompts(scenes)
    }
    
    return NarrationVideoResult(
        scenes=scenes,
        metadata=metadata
    )

4. PLAN TIERS & FEATURE GATING
4.1 Plan Structure
typescriptenum PlanTier {
  FREE = 'free',
  CREATOR_LITE = 'creator_lite',
  CREATOR_PRO = 'creator_pro',
  ENTERPRISE = 'enterprise'  // Future
}

interface PlanFeatures {
  // Core Limits
  monthlyMinutes: number;        // Audio minutes per month
  maxProjectSize: number;        // Minutes per project
  maxProjects: number;           // Active projects
  storageGB: number;             // Storage limit
  
  // Features
  dashboardAccess: boolean;
  studioAccess: boolean;
  watermarkFree: boolean;
  
  // Audio Quality
  maxBitrate: number;            // kbps
  formats: string[];             // mp3, wav, flac
  
  // Voice Features
  presetVoices: number;          // Available preset voices
  voiceCloning: boolean;
  voiceCloneSlots: number;       // Max cloned voices
  voiceMemory: boolean;          // Pronunciation memory
  emotionControl: 'basic' | 'advanced' | 'pro';
  
  // Advanced Features
  narrationToVideo: boolean;
  speechTranslation: boolean;
  voiceStyleTransfer: boolean;
  audioEnhancement: boolean;
  ssmlSupport: boolean;
  
  // Processing
  priority: 'low' | 'medium' | 'high';
  concurrentJobs: number;        // Simultaneous processing
  batchProcessing: boolean;
  
  // Collaboration (Future)
  teamSeats: number;
  sharing: boolean;
  apiAccess: boolean;
  
  // Support
  supportTier: 'community' | 'email' | 'priority';
}
4.2 Plan Comparison
FeatureFreeCreator LiteCreator ProPrice$0/mo$19/mo$49/moMonthly Minutes30 min300 min1000 minMax Project Size5 min30 minUnlimitedActive Projects325UnlimitedStorage500MB5GB25GBDashboard Access✅✅✅Creator Studio❌✅✅WatermarkYesNoNoAudio Bitrate128kbps192kbps320kbpsFormatsMP3MP3, WAVMP3, WAV, FLACPreset Voices52050+Voice Cloning❌✅ (2 slots)✅ (10 slots)Voice Memory❌❌✅Emotion ControlBasic (4)Advanced (12)Pro (Custom)Narration-to-Video❌✅✅Speech Translation❌❌✅Style Transfer❌❌✅SSML Support❌LimitedFullPriority ProcessingLowMediumHighConcurrent Jobs125SupportCommunityEmailPriority
4.3 Feature Gating Implementation
typescript// Backend - Supabase Edge Function
export async function checkFeatureAccess(
  userId: string,
  feature: string
): Promise<FeatureAccessResult> {
  // Get user's current plan
  const { data: profile } = await supabase
    .from('profiles')
    .select('plan_tier, subscription_status, usage_this_month')
    .eq('id', userId)
    .single();
  
  if (!profile) throw new Error('User not found');
  
  // Check subscription status
  if (profile.subscription_status !== 'active' && profile.plan_tier !== 'free') {
    return {
      allowed: false,
      reason: 'subscription_inactive',
      message: 'Your subscription is inactive. Please update your payment method.',
      redirectUrl: '/billing'
    };
  }
  
  // Get plan features
  const planFeatures = PLAN_FEATURES[profile.plan_tier];
  
  // Check specific feature access
  switch (feature) {
    case 'studio_access':
      if (!planFeatures.studioAccess) {
        return {
          allowed: false,
          reason: 'plan_upgrade_required',
          message: 'Creator Studio is available on Creator Lite and Pro plans.',
          requiredPlan: 'creator_lite',
          upgradeUrl: '/upgrade?feature=studio'
        };
      }
      break;
    
    case 'voice_cloning':
      if (!planFeatures.voiceCloning) {
        return {
          allowed: false,
          reason: 'plan_upgrade_required',
          message: 'Voice cloning requires Creator Lite or Pro plan.',
          requiredPlan: 'creator_lite',
          upgradeUrl: '/upgrade?feature=voice_cloning'
        };
      }
      
      // Check if user has reached voice clone slots
      const { count: voiceCount } = await supabase
        .from('voice_profiles')
        .select('id', { count: 'exact' })
        .eq('user_id', userId);
      
      if (voiceCount >= planFeatures.voiceCloneSlots) {
        return {
          allowed: false,
          reason: 'limit_reached',
          message: `You've reached your limit of ${planFeatures.voiceCloneSlots} cloned voices.`,
          action: 'upgrade_or_delete',
          upgradeUrl: '/upgrade?feature=voice_slots'
        };
      }
      break;
    
    case 'create_job':
      // Check monthly minutes limit
      if (profile.usage_this_month >= planFeatures.monthlyMinutes) {
        return {
          allowed: false,
          reason: 'quota_exceeded',
          message: `You've used ${profile.usage_this_month} of ${planFeatures.monthlyMinutes} minutes this month.`,
          resetDate: getNextMonthResetDate(),
          upgradeUrl: '/upgrade?feature=minutes'
        };
      }
      
      // Check concurrent jobs
      const { count: activeJobs } = await supabase
        .from('jobs')
        .select('id', { count: 'exact' })
        .eq('user_id', userId)
        .in('status', ['pending', 'processing']);
      
      if (activeJobs >= planFeatures.concurrentJobs) {
        return {
          allowed: false,
          reason: 'concurrent_limit',
          message: `You can process ${planFeatures.concurrentJobs} job(s) at a time.`,
          action: 'wait_or_upgrade'
        };
      }
      break;
  }
  
  return {
    allowed: true,
    message: 'Feature access granted'
  };
}

5. DATABASE SCHEMA
5.1 Core Tables
sql-- Users and Authentication (managed by Supabase Auth)
-- Extends auth.users with profile information

CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  display_name TEXT,
  avatar_url TEXT,
  plan_tier TEXT NOT NULL DEFAULT 'free',
  subscription_status TEXT NOT NULL DEFAULT 'active', -- active, past_due, canceled, trialing
  subscription_id TEXT, -- Stripe subscription ID
  trial_ends_at TIMESTAMPTZ,
  
  -- Usage tracking
  usage_this_month INTEGER DEFAULT 0, -- Minutes generated
  usage_reset_date TIMESTAMPTZ DEFAULT DATE_TRUNC('month', NOW() + INTERVAL '1 month'),
  storage_used_bytes BIGINT DEFAULT 0,
  
  -- Quick Jobs tracking
  quick_job_used BOOLEAN DEFAULT FALSE,
  quick_job_fingerprints JSONB DEFAULT '[]',
  
  -- Preferences
  default_language TEXT DEFAULT 'en',
  default_voice_id TEXT,
  preferences JSONB DEFAULT '{}',
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  last_active_at TIMESTAMPTZ DEFAULT NOW()
);

-- Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own profile" ON profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid() = id);

-- Projects
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  type TEXT NOT NULL DEFAULT 'studio', -- studio, simple, narration_video
  
  -- Project data
  settings JSONB DEFAULT '{}', -- Voice defaults, quality settings
  thumbnail_url TEXT,
  duration_seconds INTEGER DEFAULT 0,
  
  -- Status
  is_archived BOOLEAN DEFAULT FALSE,
  last_opened_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_last_opened ON projects(last_opened_at DESC);

ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own projects" ON projects FOR ALL USING (auth.uid() = user_id);

-- Narration Blocks (Studio Timeline)
CREATE TABLE narration_blocks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  
  -- Block properties
  block_order INTEGER NOT NULL,
  block_type TEXT NOT NULL DEFAULT 'narration', -- narration, pause, music, sfx
  
  -- Content
  content_text TEXT,
  ssml_content TEXT,
  pause_duration_ms INTEGER, -- For pause blocks
  
  -- Voice settings
  voice_id TEXT NOT NULL,
  voice_type TEXT NOT NULL DEFAULT 'preset', -- preset, cloned, custom
  emotion TEXT DEFAULT 'neutral',
  speed NUMERIC(3,2) DEFAULT 1.0,
  pitch INTEGER DEFAULT 0,
  volume INTEGER DEFAULT 100,
  
  -- Linked assets
  image_id UUID REFERENCES assets(id) ON DELETE SET NULL,
  video_id UUID REFERENCES assets(id) ON DELETE SET NULL,
  background_music_id UUID REFERENCES assets(id) ON DELETE SET NULL,
  
  -- Generated output
  generated_audio_url TEXT,
  waveform_data JSONB, -- Array of amplitude values for visualization
  duration_seconds NUMERIC(10,2),
  
  -- Metadata
  is_locked BOOLEAN DEFAULT FALSE,
  regeneration_count INTEGER DEFAULT 0,
  last_regenerated_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_narration_blocks_project ON narration_blocks(project_id, block_order);
CREATE INDEX idx_narration_blocks_user ON narration_blocks(user_id);

ALTER TABLE narration_blocks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own blocks" ON narration_blocks FOR ALL USING (auth.uid() = user_id);

-- Jobs (AI Processing Queue)
CREATE TABLE jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  job_type TEXT NOT NULL, -- text_to_speech, voice_clone, translation, etc.
  
  -- Status
  status TEXT NOT NULL DEFAULT 'pending', -- pending, queued, processing, completed, failed, cancelled
  progress INTEGER DEFAULT 0, -- 0-100
  progress_message TEXT,
  queue_position INTEGER,
  estimated_time_seconds INTEGER,
  
  -- Priority (based on user plan)
  priority INTEGER DEFAULT 3, -- 1=high (pro), 2=medium (lite), 3=low (free)
  
  -- Input data
  input_data JSONB NOT NULL,
  
  -- Output
  result_data JSONB,
  result_urls JSONB, -- Array of generated file URLs
  
  -- Error handling
  error_code TEXT,
  error_message TEXT,
  is_retryable BOOLEAN DEFAULT TRUE,
  retry_count INTEGER DEFAULT 0,
  max_retries INTEGER DEFAULT 3,
  
  -- Relationships
  project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
  narration_block_id UUID REFERENCES narration_blocks(id) ON DELETE SET NULL,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '7 days' -- Result cleanup
);

CREATE INDEX idx_jobs_user_id ON jobs(user_id);
CREATE INDEX idx_jobs_status ON jobs(status) WHERE status IN ('pending', 'processing');
CREATE INDEX idx_jobs_priority ON jobs(priority, created_at) WHERE status = 'pending';
CREATE INDEX idx_jobs_expires_at ON jobs(expires_at) WHERE status = 'completed';

ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own jobs" ON jobs FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can cancel own jobs" ON jobs FOR UPDATE USING (auth.uid() = user_id AND status IN ('pending', 'queued'));

-- Assets (Images, Videos, Audio)
CREATE TABLE assets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  
  -- Asset info
  asset_type TEXT NOT NULL, -- image, video, audio, music
  filename TEXT NOT NULL,
  storage_url TEXT NOT NULL,
  storage_path TEXT NOT NULL, -- Path in Supabase Storage
  
  -- Metadata
  file_size_bytes BIGINT NOT NULL,
  format TEXT NOT NULL, -- mp3, wav, png, mp4, etc.
  duration_seconds NUMERIC(10,2), -- For audio/video
  resolution_width INTEGER, -- For images/video
  resolution_height INTEGER,
  
  -- Organization
  tags TEXT[] DEFAULT '{}',
  is_ai_generated BOOLEAN DEFAULT FALSE,
  generation_prompt TEXT, -- If AI-generated
  
  -- Usage tracking
  linked_blocks_count INTEGER DEFAULT 0,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_assets_user_id ON assets(user_id);
CREATE INDEX idx_assets_type ON assets(asset_type);
CREATE INDEX idx_assets_tags ON assets USING GIN(tags);

ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own assets" ON assets FOR ALL USING (auth.uid() = user_id);

-- Voice Profiles (Cloned Voices)
CREATE TABLE voice_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  
  -- Voice info
  name TEXT NOT NULL,
  description TEXT,
  voice_type TEXT NOT NULL DEFAULT 'cloned', -- cloned, custom
  
  -- Model data
  model_storage_path TEXT NOT NULL, -- Path to voice model in storage
  sample_audio_urls JSONB NOT NULL, -- Training samples
  
  -- Metadata
  training_duration_seconds INTEGER,
  voice_characteristics JSONB, -- Pitch, tone, accent, etc.
  quality_score NUMERIC(3,2),
  
  -- Legal
  consent_granted BOOLEAN NOT NULL DEFAULT FALSE,
  consent_timestamp TIMESTAMPTZ,
  consent_ip_address INET,
  
  -- Usage tracking
  usage_count INTEGER DEFAULT 0,
  last_used_at TIMESTAMPTZ,
  
  -- Status
  is_active BOOLEAN DEFAULT TRUE,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_voice_profiles_user ON voice_profiles(user_id) WHERE is_active = TRUE;

ALTER TABLE voice_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own voices" ON voice_profiles FOR ALL USING (auth.uid() = user_id);

-- Pronunciation Memory
CREATE TABLE pronunciation_memory (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  
  -- Word info
  word TEXT NOT NULL,
  ipa_pronunciation TEXT, -- International Phonetic Alphabet
  custom_spelling TEXT,
  context TEXT, -- "medical term", "brand name", etc.
  
  -- Example audio
  audio_example_url TEXT, -- User-uploaded correct pronunciation
  
  -- Usage tracking
  applied_to_projects UUID[] DEFAULT '{}',
  usage_count INTEGER DEFAULT 0,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(user_id, word)
);

CREATE INDEX idx_pronunciation_user_word ON pronunciation_memory(user_id, word);

ALTER TABLE pronunciation_memory ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own pronunciations" ON pronunciation_memory FOR ALL USING (auth.uid() = user_id);

-- Usage Logs (Analytics & Billing)
CREATE TABLE usage_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  
  -- Usage type
  usage_type TEXT NOT NULL, -- tts, voice_clone, translation, storage
  
  -- Metrics
  minutes_used NUMERIC(10,2),
  characters_processed INTEGER,
  storage_bytes BIGINT,
  
  -- Context
  job_id UUID REFERENCES jobs(id) ON DELETE SET NULL,
  project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
  
  -- Billing
  plan_tier TEXT NOT NULL,
  is_billable BOOLEAN DEFAULT TRUE,
  
  -- Timestamp
  logged_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_usage_logs_user_date ON usage_logs(user_id, logged_at DESC);
CREATE INDEX idx_usage_logs_monthly ON usage_logs(user_id, DATE_TRUNC('month', logged_at));

-- No RLS needed (internal table, accessed via functions)

-- Subscription Events (Stripe Webhooks)
CREATE TABLE subscription_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
  
  -- Stripe data
  stripe_event_id TEXT NOT NULL UNIQUE,
  stripe_event_type TEXT NOT NULL,
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  
  -- Event data
  event_data JSONB NOT NULL,
  
  -- Processing
  processed BOOLEAN DEFAULT FALSE,
  processed_at TIMESTAMPTZ,
  error_message TEXT,
  
  -- Timestamp
  received_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_subscription_events_processed ON subscription_events(processed) WHERE processed = FALSE;

-- No RLS (internal table)
5.2 Storage Buckets
typescript// Supabase Storage Buckets Configuration

const STORAGE_BUCKETS = {
  // User-generated audio outputs
  'audio-outputs': {
    public: false, // Private, signed URLs only
    fileSizeLimit: 50 * 1024 * 1024, // 50MB
    allowedMimeTypes: ['audio/mpeg', 'audio/wav', 'audio/flac', 'audio/ogg'],
    path: 'users/{userId}/outputs/{jobId}.{ext}'
  },
  
  // Voice model files (cloned voices)
  'voice-models': {
    public: false,
    fileSizeLimit: 500 * 1024 * 1024, // 500MB
    allowedMimeTypes: ['application/octet-stream', 'application/x-tar'],
    path: 'users/{userId}/voices/{voiceId}/model.tar'
  },
  
  // Voice training samples
  'voice-samples': {
    public: false,
    fileSizeLimit: 100 * 1024 * 1024, // 100MB
    allowedMimeTypes: ['audio/mpeg', 'audio/wav', 'audio/flac'],
    path: 'users/{userId}/voices/{voiceId}/samples/{filename}'
  },
  
  // User-uploaded assets (images, videos)
  'user-assets': {
    public: false,
    fileSizeLimit: 200 * 1024 * 1024, // 200MB
    allowedMimeTypes: [
      'image/jpeg', 'image/png', 'image/webp', 'image/gif',
      'video/mp4', 'video/quicktime', 'video/x-msvideo',
      'audio/mpeg', 'audio/wav'
    ],
    path: 'users/{userId}/assets/{assetId}.{ext}'
  },
  
  // Temporary uploads (for processing)
  'temp-uploads': {
    public: false,
    fileSizeLimit: 100 * 1024 * 1024, // 100MB
    allowedMimeTypes: ['*'],
    path: 'temp/{userId}/{timestamp}/{filename}',
    autoDelete: '24 hours' // Automatic cleanup
  },
  
  // User avatars
  'avatars': {
    public: true,
    fileSizeLimit: 5 * 1024 * 1024, // 5MB
    allowedMimeTypes: ['image/jpeg', 'image/png', 'image/webp'],
    path: 'avatars/{userId}.{ext}'
  }
};

// Storage Policies (Row Level Security for Storage)
// Users can only access their own files

CREATE POLICY "Users can upload own files"
  ON storage.objects FOR INSERT
  WITH CHECK (
    bucket_id IN ('audio-outputs', 'voice-models', 'voice-samples', 'user-assets', 'temp-uploads', 'avatars')
    AND (storage.foldername(name))[1] = auth.uid()::text
  );

CREATE POLICY "Users can read own files"
  ON storage.objects FOR SELECT
  USING (
    bucket_id IN ('audio-outputs', 'voice-models', 'voice-samples', 'user-assets', 'temp-uploads', 'avatars')
    AND (storage.foldername(name))[1] = auth.uid()::text
  );

CREATE POLICY "Users can delete own files"
  ON storage.objects FOR DELETE
  USING (
    bucket_id IN ('audio-outputs', 'voice-models', 'voice-samples', 'user-assets', 'temp-uploads', 'avatars')
    AND (storage.foldername(name))[1] = auth.uid()::text
  );

6. UI/UX DESIGN RECOMMENDATIONS
6.1 Design System Approach
Recommended: Design Token System with CSS Variables
This provides maximum flexibility, maintainability, and allows for easy theming without CSS-in-JS overhead.
css/* design-tokens.css */

:root {
  /* Color Palette */
  --color-primary-50: #f0f4ff;
  --color-primary-100: #dce5ff;
  --color-primary-500: #4f46e5;
  --color-primary-600: #4338ca;
  --color-primary-900: #1e1b4b;
  
  --color-neutral-50: #fafafa;
  --color-neutral-100: #f4f4f5;
  --color-neutral-500: #71717a;
  --color-neutral-900: #18181b;
  
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  
  /* Typography */
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'Fira Code', monospace;
  
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;
  
  /* Spacing */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-12: 3rem;
  --space-16: 4rem;
  
  /* Border Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-full: 9999px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
  
  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-base: 250ms ease;
  --transition-slow: 350ms ease;
  
  /* Z-Index Scale */
  --z-base: 0;
  --z-dropdown: 1000;
  --z-sticky: 1100;
  --z-modal: 1300;
  --z-popover: 1400;
  --z-tooltip: 1500;
}

/* Dark Mode Tokens */
[data-theme="dark"] {
  --color-neutral-50: #18181b;
  --color-neutral-100: #27272a;
  --color-neutral-500: #a1a1aa;
  --color-neutral-900: #fafafa;
}
6.2 10 Modern UI Pattern Styles for Speecher
1. Neumorphism (Soft UI) ⭐ Recommended for Dashboard
Why it works: Creates a gentle, tactile interface that feels approachable for casual users. The soft shadows and highlights make controls feel clickable and inviting.
Where to use:

Dashboard quick generate panel
Voice/emotion selection cards
Playback controls

Example:
css.neumorphic-card {
  background: var(--color-neutral-50);
  border-radius: var(--radius-lg);
  box-shadow: 
    8px 8px 16px rgba(0, 0, 0, 0.1),
    -8px -8px 16px rgba(255, 255, 255, 0.9);
  padding: var(--space-6);
}

.neumorphic-button {
  background: linear-gradient(145deg, #f0f0f0, #cacaca);
  box-shadow:
    4px 4px 8px rgba(0, 0, 0, 0.15),
    -4px -4px 8px rgba(255, 255, 255, 0.7);
  transition: all var(--transition-base);
}

.neumorphic-button:active {
  box-shadow:
    inset 4px 4px 8px rgba(0, 0, 0, 0.15),
    inset -4px -4px 8px rgba(255, 255, 255, 0.7);
}
2. Glassmorphism ⭐ Recommended for Modals & Overlays
Why it works: Creates depth and hierarchy without being obtrusive. Perfect for overlays that need to remain contextual to what's beneath.
Where to use:

Upgrade prompts
Feature preview overlays
Settings panels
Job status notifications

Example:
css.glass-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
}
3. Brutalist/Industrial - For Creator Studio
Why it works: Communicates power, precision, and professional-grade tools. The stark, grid-based layouts help users focus on complex editing tasks.
Where to use:

Creator Studio timeline
Block editor interface
Advanced settings panels

Example:
css.studio-workspace {
  background: var(--color-neutral-900);
  color: var(--color-neutral-50);
  font-family: var(--font-mono);
  border: 2px solid var(--color-neutral-500);
  box-shadow: 4px 4px 0 var(--color-primary-500);
}

.studio-block {
  background: var(--color-neutral-800);
  border-left: 4px solid var(--color-primary-500);
  padding: var(--space-4);
  margin: var(--space-2) 0;
}
4. Card-Based Masonry Layout - For Asset Libraries
Why it works: Efficiently displays mixed media (images, videos, audio) with varying aspect ratios. Pinterest-style layouts feel familiar and browsable.
Where to use:

Asset library
Voice profile gallery
Recent outputs
Project gallery

Example:
css.masonry-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  grid-auto-rows: 10px;
  gap: var(--space-4);
}

.masonry-item {
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-md);
  transition: transform var(--transition-base);
}

.masonry-item:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}
5. Floating Action Pattern - For Quick Actions
Why it works: Keeps primary actions always accessible without cluttering the interface. Mobile-friendly and increasingly popular in web apps.
Where to use:

"New Project" button (Dashboard)
"Add Block" button (Studio)
"Upload Asset" trigger
"Help/Support" access

Example:
css.fab {
  position: fixed;
  bottom: var(--space-8);
  right: var(--space-8);
  width: 64px;
  height: 64px;
  border-radius: var(--radius-full);
  background: var(--color-primary-500);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-base);
  z-index: var(--z-sticky);
}

.fab:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(79, 70, 229, 0.6);
}
6. Progressive Disclosure - For Complex Forms
Why it works: Reduces cognitive load by showing options progressively. Essential for features like voice cloning setup and narration-to-video generation.
Where to use:

Voice cloning wizard
Narration-to-video setup
Account settings
Onboarding flows

Example:
css.wizard-step {
  opacity: 0;
  max-height: 0;
  overflow: hidden;
  transition: all var(--transition-slow);
}

.wizard-step.active {
  opacity: 1;
  max-height: 1000px;
}

.wizard-nav {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-6);
}

.wizard-dot {
  width: 12px;
  height: 12px;
  border-radius: var(--radius-full);
  background: var(--color-neutral-300);
  transition: all var(--transition-base);
}

.wizard-dot.completed {
  background: var(--color-success);
}

.wizard-dot.active {
  background: var(--color-primary-500);
  transform: scale(1.5);
}
7. Waveform Visualization Pattern - Audio-First Design
Why it works: Visually communicates audio content at a glance. Makes the platform feel audio-native and professional.
Where to use:

Timeline blocks (Studio)
Recent outputs preview
Voice sample playback
Audio comparison views

Example:
css.waveform-container {
  display: flex;
  align-items: center;
  gap: 2px;
  height: 60px;
  padding: var(--space-3);
  background: var(--color-neutral-100);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.waveform-bar {
  flex: 1;
  background: var(--color-primary-500);
  border-radius: var(--radius-sm);
  transition: height var(--transition-fast);
  opacity: 0.7;
}

.waveform-bar.playing {
  opacity: 1;
  animation: pulse 0.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(1.2); }
}
8. Command Palette / Spotlight Search - Power User Feature
Why it works: Keyboard-first navigation for experienced users. Dramatically speeds up workflow in Creator Studio.
Where to use:

Global search (Cmd/Ctrl+K)
Quick actions in Studio
Jump to project
Feature discovery

Example:
css.command-palette {
  position: fixed;
  top: 20%;
  left: 50%;
  transform: translateX(-50%);
  width: min(600px, 90vw);
  background: white;
  border-radius: var(--radius-xl);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.2);
  z-index: var(--z-modal);
  overflow: hidden;
}

.command-input {
  width: 100%;
  padding: var(--space-4);
  border: none;
  border-bottom: 1px solid var(--color-neutral-200);
  font-size: var(--text-lg);
}

.command-list {
  max-height: 400px;
  overflow-y: auto;
}

.command-item {
  padding: var(--space-3) var(--space-4);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  transition: background var(--transition-fast);
}

.command-item:hover,
.command-item.selected {
  background: var(--color-primary-50);
}

.command-kbd {
  margin-left: auto;
  padding: 2px 8px;
  background: var(--color-neutral-100);
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  font-size: var(--text-xs);
}
9. Split-Screen Editing Pattern - Studio Layout
Why it works: Essential for comparing before/after, editing while previewing, or working with reference material.
Where to use:

Studio: Timeline vs. Preview
Voice cloning: Original vs. Clone comparison
Translation: Source vs. Target

Example:
css.split-view {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
  height: 100%;
}

.split-panel {
  overflow: auto;
  position: relative;
}

.split-divider {
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 4px;
  background: var(--color-neutral-300);
  cursor: col-resize;
  transform: translateX(-50%);
  transition: background var(--transition-fast);
}

.split-divider:hover {
  background: var(--color-primary-500);
}

/* Responsive: Stack on mobile */
@media (max-width: 768px) {
  .split-view {
    grid-template-columns: 1fr;
  }
}
10. Status-Driven UI - Real-time Feedback
Why it works: Keeps users informed about long-running AI processes. Reduces anxiety and abandonment during processing.
Where to use:

Job processing indicators
Upload progress
Generation status
Export progress

Example:
css.status-card {
  background: white;
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: var(--shadow-md);
  border-left: 4px solid var(--status-color);
}

.status-card[data-status="pending"] {
  --status-color: var(--color-neutral-400);
}

.status-card[data-status="processing"] {
  --status-color: var(--color-primary-500);
}

.status-card[data-status="completed"] {
  --status-color: var(--color-success);
}

.status-card[data-status="failed"] {
  --status-color: var(--color-error);
}

.progress-bar {
  height: 8px;
  background: var(--color-neutral-200);
  border-radius: var(--radius-full);
  overflow: hidden;
  margin-top: var(--space-3);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(
    90deg,
    var(--color-primary-500),
    var(--color-primary-600)
  );
  border-radius: var(--radius-full);
  transition: width var(--transition-slow);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.status-message {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-2);
  font-size: var(--text-sm);
  color: var(--color-neutral-600);
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-neutral-300);
  border-top-color: var(--color-primary-500);
  border-radius: var(--radius-full);
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

---

### 6.3 Recommended CSS Implementation Strategy
```
/styles
  /tokens
    colors.css
    typography.css
    spacing.css
    effects.css
  /base
    reset.css
    global.css
  /components
    buttons.module.css
    cards.module.css
    forms.module.css
    modals.module.css
  /layouts
    dashboard.module.css
    studio.module.css
  /patterns
    neumorphism.module.css
    glassmorphism.module.css
    waveform.module.css
Component Example:
typescript// components/Button/Button.tsx
import styles from './Button.module.css';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'neumorphic';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
}

export function Button({ variant = 'primary', size = 'md', children, onClick }: ButtonProps) {
  return (
    <button 
      className={`${styles.button} ${styles[variant]} ${styles[size]}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
css/* Button.module.css */
.button {
  font-family: var(--font-sans);
  font-weight: 600;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-base);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
}

.sm {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
}

.md {
  padding: var(--space-3) var(--space-6);
  font-size: var(--text-base);
}

.lg {
  padding: var(--space-4) var(--space-8);
  font-size: var(--text-lg);
}

.primary {
  background: var(--color-primary-500);
  color: white;
}

.primary:hover {
  background: var(--color-primary-600);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.secondary {
  background: var(--color-neutral-200);
  color: var(--color-neutral-900);
}

.neumorphic {
  background: linear-gradient(145deg, #f0f0f0, #cacaca);
  box-shadow:
    4px 4px 8px rgba(0, 0, 0, 0.15),
    -4px -4px 8px rgba(255, 255, 255, 0.7);
  color: var(--color-neutral-900);
}

.neumorphic:active {
  box-shadow:
    inset 4px 4px 8px rgba(0, 0, 0, 0.15),
    inset -4px -4px 8px rgba(255, 255, 255, 0.7);
}
```

---

## 7. PAGE STRUCTURE & ROUTING

### 7.1 Next.js App Router Structure
```
/app
  /(public)
    /page.tsx                    # Landing page
    /quick
      /text-to-speech/page.tsx   # Quick Job: TTS
      /transcription/page.tsx    # Quick Job: Transcription
      /translation/page.tsx      # Quick Job: Translation
    /pricing/page.tsx            # Pricing page
    /about/page.tsx
    
  /(auth)
    /login/page.tsx
    /signup/page.tsx
    /forgot-password/page.tsx
    /reset-password/page.tsx
    
  /(dashboard)                   # Protected routes
    /layout.tsx                  # Dashboard shell (sidebar, header)
    /page.tsx                    # Main dashboard
    /projects
      /page.tsx                  # Project list
      /[id]/page.tsx            # Project detail (redirects to Studio)
    /studio
      /[projectId]/page.tsx      # Creator Studio workspace
    /settings
      /page.tsx                  # Account settings
      /profile/page.tsx
      /billing/page.tsx
      /preferences/page.tsx
    /upgrade/page.tsx
    
  /api
    /auth
      /callback/route.ts         # Auth callback
    /jobs
      /create/route.ts           # Create AI job
      /[id]/route.ts            # Get job status
      /[id]/cancel/route.ts     # Cancel job
    /projects
      /route.ts                  # CRUD projects
      /[id]/route.ts
      /[id]/blocks/route.ts     # Narration blocks
    /assets
      /route.ts                  # Upload/list assets
      /[id]/route.ts            # Asset operations
    /voices
      /route.ts                  # Voice profiles
      /[id]/route.ts
    /webhooks
      /stripe/route.ts           # Stripe webhooks
      /supabase/route.ts         # Supabase webhooks
      /python-service/route.ts   # Job updates from Python
7.2 Key Page Specifications
Landing Page (/)

Hero section with Quick Job CTA
Feature showcase (TTS, Studio, Voices)
Social proof / testimonials
Pricing teaser
FAQ
Footer with links

Quick Jobs (/quick/*)

Minimal UI, focused on single task
File upload or text input
Real-time processing status
Result preview
"Sign up to save" prompt
No navigation clutter

Main Dashboard (/dashboard)

Quick generate panel (prominent)
Recent outputs grid
Usage stats card
Upgrade prompts (contextual)
Project shortcuts
Navigation sidebar

Creator Studio (/studio/[projectId])

Full-screen workspace
Three-column layout: Assets | Timeline | Properties
Persistent auto-save indicator
Command palette (Cmd+K)
Export options
Keyboard shortcuts help (?)

Settings Pages (/settings/*)

Tabbed interface
Profile: Avatar, name, email
Billing: Subscription, usage, invoices
Preferences: Default voice, language, notifications

Upgrade Page (/upgrade)

Plan comparison table
Feature highlights
FAQs
"Start trial" vs "Subscribe now"
Money-back guarantee badge


8. AUTHENTICATION & AUTHORIZATION
8.1 Supabase Auth Implementation
typescript// lib/supabase/client.ts
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import { Database } from '@/types/supabase';

export const createClient = () => createClientComponentClient<Database>();

// lib/supabase/server.ts
import { createServerComponentClient } from '@supabase/auth-helpers-nextjs';
import { cookies } from 'next/headers';
import { Database } from '@/types/supabase';

export const createServerClient = () =>
  createServerComponentClient<Database>({ cookies });

// middleware.ts (Route protection)
import { createMiddlewareClient } from '@supabase/auth-helpers-nextjs';
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export async function middleware(req: NextRequest) {
  const res = NextResponse.next();
  const supabase = createMiddlewareClient({ req, res });
  
  const { data: { session } } = await supabase.auth.getSession();
  
  // Protect dashboard routes
  if (req.nextUrl.pathname.startsWith('/dashboard') && !session) {
    return NextResponse.redirect(new URL('/login', req.url));
  }
  
  // Protect Studio routes + check plan
  if (req.nextUrl.pathname.startsWith('/studio')) {
    if (!session) {
      return NextResponse.redirect(new URL('/login', req.url));
    }
    
    const { data: profile } = await supabase
      .from('profiles')
      .select('plan_tier, subscription_status')
      .eq('id', session.user.id)
      .single();
    
    if (profile?.plan_tier === 'free' || profile?.subscription_status !== 'active') {
      return NextResponse.redirect(new URL('/upgrade?feature=studio', req.url));
    }
  }
  
  return res;
}

export const config = {
  matcher: ['/dashboard/:path*', '/studio/:path*', '/settings/:path*'],
};
8.2 Row Level Security (RLS) Enforcement
All database tables use RLS policies to ensure users can only access their own data. This is enforced at the database level, not just in application code.
Critical Security Rules:

Never disable RLS on user-facing tables
Always use auth.uid() in policies to filter by user
Test policies with different user contexts
Audit logs for unauthorized access attempts
Rate limiting on API routes (via Edge Functions)


9. DEPLOYMENT STRATEGY
9.1 Next.js Deployment (Vercel)
yaml# vercel.json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "regions": ["iad1", "sfo1"],  # US East & West
  "env": {
    "NEXT_PUBLIC_SUPABASE_URL": "@supabase-url",
    "NEXT_PUBLIC_SUPABASE_ANON_KEY": "@supabase-anon-key",
    "SUPABASE_SERVICE_ROLE_KEY": "@supabase-service-key",
    "PYTHON_SERVICE_URL": "@python-service-url",
    "PYTHON_SERVICE_SECRET": "@python-service-secret",
    "STRIPE_SECRET_KEY": "@stripe-secret",
    "STRIPE_WEBHOOK_SECRET": "@stripe-webhook-secret"
  }
}
Deployment Process:

Push to main branch on GitHub
Vercel auto-builds and deploys
Preview deployments for PRs
Environment variables managed in Vercel dashboard
Edge Functions for rate limiting, validation

9.2 Python Service Deployment (Hostinger VPS)
Server Specifications:

Minimum: 8 CPU cores, 32GB RAM, 200GB SSD
Recommended: 16 CPU cores, 64GB RAM, 500GB NVMe SSD
OS: Ubuntu 24.04 LTS
Docker: Latest stable
Python: 3.11+

Docker Compose Setup:
yaml# docker-compose.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
  
  celery-worker:
    build:
      context: .
      dockerfile: Dockerfile.worker
    restart: always
    environment:
      - REDIS_URL=redis://redis:6379/0
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
      - MODEL_CACHE_DIR=/models
    volumes:
      - ./models:/models
      - ./temp:/temp
    depends_on:
      - redis
    deploy:
      replicas: 4  # Scale based on load
      resources:
        limits:
          cpus: '2'
          memory: 8G
        reservations:
          cpus: '1'
          memory: 4G
  
  celery-beat:
    build:
      context: .
      dockerfile: Dockerfile.beat
    restart: always
    environment:
      - REDIS_URL=redis://redis:6379/0
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
    depends_on:
      - redis
  
  api-server:
    build:
      context: .
      dockerfile: Dockerfile.api
    restart: always
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
      - API_SECRET_KEY=${API_SECRET_KEY}
    depends_on:
      - redis
      - celery-worker

volumes:
  redis_data:
Deployment Steps:

SSH into VPS
Pull latest code from GitHub
Build Docker images: docker-compose build
Run migrations (if any)
Start services: docker-compose up -d
Monitor logs: docker-compose logs -f
Scale workers as needed: docker-compose up -d --scale celery-worker=8

Monitoring & Alerting:

Use Flower for Celery monitoring
Set up Prometheus + Grafana for metrics
Configure alerts for:

High queue length (>100 jobs)
Worker failures
High memory usage (>90%)
Disk space low (<20%)



9.3 CI/CD Pipeline
yaml# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check
      - run: npm test
  
  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest
      - run: mypy .
  
  deploy-frontend:
    needs: [test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          vercel-args: '--prod'
  
  deploy-python:
    needs: [test-python]
    runs-on: ubuntu-Continue17:38latest
if: github.ref == 'refs/heads/main'
steps:
- uses: actions/checkout@v3
- name: Deploy to VPS
uses: appleboy/ssh-action@master
with:
host: ${{ secrets.VPS_HOST }}
username: ${{ secrets.VPS_USERNAME }}
key: ${{ secrets.VPS_SSH_KEY }}
script: |
cd /opt/speecher-python
git pull origin main
docker-compose build
docker-compose up -d

---

## 10. MONITORING & ANALYTICS

### 10.1 Application Monitoring

**Frontend (Vercel Analytics)**
- Page load times
- Core Web Vitals
- Error tracking (via Sentry)
- User flows (via PostHog)

**Backend (Python Service)**
- Job queue length
- Processing times per job type
- Success/failure rates
- Model load times
- Memory usage per worker

**Database (Supabase)**
- Query performance
- Connection pool usage
- Storage consumption
- API request rates

### 10.2 Business Analytics

**Key Metrics to Track:**
1. **Acquisition:**
   - Quick Job completion rate
   - Quick Job → Signup conversion
   - Signup sources (organic, paid, referral)

2. **Activation:**
   - Time to first generation (dashboard)
   - Dashboard → Studio upgrade rate
   - Feature adoption rates

3. **Retention:**
   - Daily/Weekly/Monthly active users
   - Churn rate by plan tier
   - Re-engagement campaigns effectiveness

4. **Revenue:**
   - MRR (Monthly Recurring Revenue)
   - ARPU (Average Revenue Per User)
   - Upgrade rate (Free → Lite → Pro)
   - Lifetime Value (LTV)

5. **Product Usage:**
   - Minutes generated per user
   - Most popular voices
   - Feature usage (voice cloning, translation, etc.)
   - Average project duration
   - Studio session length

---

## 11. SECURITY CONSIDERATIONS

### 11.1 Data Protection

**User Data:**
- All audio outputs encrypted at rest (AES-256)
- Voice models access controlled via signed URLs
- PII (Personally Identifiable Information) isolated
- GDPR compliance: Right to deletion, data export

**API Security:**
- Rate limiting on all endpoints
- Request validation via Zod schemas
- CORS policies (whitelist only)
- API keys rotated quarterly

### 11.2 Abuse Prevention

**Quick Jobs:**
- IP-based rate limiting
- CAPTCHA after 2 failed fingerprint checks
- Honeypot fields in forms
- File upload validation (magic bytes, not extensions)

**Voice Cloning:**
- Consent checkbox with timestamp
- Audio analysis for deepfake detection
- Abuse reporting mechanism
- Admin review queue for suspicious clones

**General:**
- CSP (Content Security Policy) headers
- XSS protection
- CSRF tokens
- SQL injection prevention (parameterized queries)

---

## 12. SCALING ROADMAP

### Phase 1: MVP (Months 1-3)
- Quick Jobs (all three)
- Dashboard (basic TTS)
- Creator Studio (timeline editing)
- Free + Creator Lite plans
- Payment integration (Stripe)

### Phase 2: Growth (Months 4-6)
- Voice cloning
- Narration-to-video intelligence
- Creator Pro plan
- Mobile responsive improvements
- API beta (for Pro users)

### Phase 3: Scale (Months 7-12)
- Team/Enterprise plans
- Collaboration features
- White-label options
- Advanced analytics dashboard
- Marketplace for voices/templates

### Phase 4: Expansion (Year 2+)
- Multi-language expansion (30+ languages)
- Real-time collaboration (multiplayer Studio)
- AI voice director (auto-suggests emotion/pacing)
- Video editing integration (Adobe, Premiere Pro)
- Mobile apps (iOS, Android)

---

**END OF BLUEPRINT**

---

This blueprint provides a comprehensive, production-ready foundation for Speecher. When you're ready, say "NEXT" and I'll proceed to create the **BMAD-METHOD AI Development Prompts** that will guide the actual implementation of this system using the BMAD framework's 21 specialized agents and 50+ workflows. Sonnet 4.5Claude is AI and can make mistakes. Please double-check responses.