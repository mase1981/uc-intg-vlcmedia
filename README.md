# VLC Media Player Integration for Unfolded Circle Remote 2/3

Control your VLC Media Player instances directly from your Unfolded Circle Remote 2 or Remote 3 with comprehensive media player functionality including **album artwork** and **rich metadata**.

![VLC](https://img.shields.io/badge/VLC-Media%20Player-orange)
![License](https://img.shields.io/badge/license-MPL--2.0-blue)
[![Discord](https://badgen.net/discord/online-members/zGVYf58)](https://discord.gg/zGVYf58)
![GitHub Release](https://img.shields.io/github/v/release/mase1981/uc-intg-vlcmedia)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/mase1981/uc-intg-vlcmedia/total)
[![Buy Me A Coffee](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg)](https://buymeacoffee.com/meirmiyara)
[![PayPal](https://img.shields.io/badge/PayPal-donate-blue.svg)](https://paypal.me/mmiyara)
[![Github Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-30363D?&logo=GitHub-Sponsors&logoColor=EA4AAA)](https://github.com/sponsors/mase1981/button)

## Features

This integration provides full control of VLC Media Player with rich media information display directly from your Unfolded Circle Remote.

### 🎵 **Media Player Control**

#### **Playback Control**
- **Play/Pause Toggle** - Seamless playback control
- **Previous/Next Track** - Navigate through playlist
- **Fast Forward/Rewind** - 30-second skip controls
- **Seek** - Jump to any position in media

#### **Volume Control**
- **Volume Up/Down** - Adjust volume levels
- **Set Volume** - Direct volume control
- **Mute Toggle** - Quick mute/unmute

### 📺 **Rich Media Information Display**

#### **Dynamic Metadata**
Real-time display of media information from file tags:
- **Media Title** - Song/video title from ID3/metadata tags
- **Artist** - Artist name from file metadata
- **Album** - Album name from file metadata
- **Album Artwork** - High-quality album art display via VLC HTTP interface
- **Progress Information** - Current position and total duration
- **Playback State** - Playing, paused, stopped indicators

#### **Multi-Device Support**
- **Multiple VLC Instances** - Control VLC on different devices
- **Individual Configuration** - Separate setup for each VLC player
- **Unique Device Names** - Name each instance (Living Room PC, NVIDIA Shield, etc.)

### **VLC Requirements**
- **VLC Version**: 3.0.0 or higher (HTTP interface available)
- **HTTP Interface**: Must be enabled in VLC preferences
- **Network Access**: VLC must be accessible on local network
- **Password**: HTTP interface password must be configured

### **Network Requirements**
- **Local Network Access** - Integration requires same network as VLC
- **HTTP Port** - Default 8080 (configurable)
- **Firewall Configuration** - Ensure VLC HTTP port is accessible

## Installation

### Option 1: Remote Web Interface (Recommended)
1. Navigate to the [**Releases**](https://github.com/mase1981/uc-intg-vlc/releases) page
2. Download the latest `uc-intg-vlc-<version>.tar.gz` file
3. Open your remote's web interface (`http://your-remote-ip`)
4. Go to **Settings** → **Integrations** → **Add Integration**
5. Click **Upload** and select the downloaded `.tar.gz` file

### Option 2: Docker (Advanced Users)

The integration is available as a pre-built Docker image from GitHub Container Registry:

**Image**: `ghcr.io/mase1981/uc-intg-vlc:latest`

**Docker Compose:**
```yaml
services:
  uc-intg-vlc:
    image: ghcr.io/mase1981/uc-intg-vlc:latest
    container_name: uc-intg-vlc
    network_mode: host
    volumes:
      - </local/path>:/config
    environment:
      - UC_INTEGRATION_HTTP_PORT=9090
    restart: unless-stopped
```

**Docker Run:**
```bash
docker run -d --name=uc-intg-vlc --network host -v </local/path>:/config --restart unless-stopped ghcr.io/mase1981/uc-intg-vlc:latest
```

## Configuration

### Step 1: Enable VLC HTTP Interface

**IMPORTANT**: VLC HTTP interface **MUST** be enabled before adding the integration.

#### On Windows/Linux:
1. Open VLC
2. Go to **Tools** → **Preferences**
3. Click **Show settings: All** (bottom left)
4. Navigate to **Interface** → **Main interfaces**
5. Check **"Web"** checkbox
6. Navigate to **Interface** → **Main interfaces** → **Lua**
7. Set **"Lua HTTP Password"** (REQUIRED - remember this password)
8. Restart VLC

#### On macOS:
1. Open VLC
2. Go to **VLC** → **Preferences**
3. Click **Show All** (bottom left)
4. Navigate to **Interface** → **Main interfaces**
5. Check **"Web"** checkbox
6. Navigate to **Interface** → **Main interfaces** → **Lua**
7. Set **"Lua HTTP Password"** (REQUIRED)
8. Restart VLC

#### Verify HTTP Interface:
Open browser and visit: `http://YOUR_DEVICE_IP:8080`
- You should see a login prompt
- Username: (leave blank)
- Password: (your configured password)

### Step 2: Setup Integration

1. After installation, go to **Settings** → **Integrations**
2. The VLC integration should appear in **Available Integrations**
3. Click **"Configure"** and follow the setup wizard:

   **Device Configuration:**
   - **VLC Player IP Address**: IP of device running VLC (e.g., 192.168.1.100)
   - **HTTP Port**: VLC HTTP port (default: 8080)
   - **Password**: Password you set in VLC Lua HTTP settings
   - **Device Name**: Friendly name (e.g., "Living Room PC", "NVIDIA Shield")

4. Click **"Complete Setup"** when connection is successful
5. Media player entity will be created for the device


### Step 3: Add Entities to Activities

1. Go to **Activities** in your remote interface
2. Edit or create an activity
3. Add VLC entities from **Available Entities** list:
   - **[Device Name]** - Media player control interface
4. Configure button mappings and UI layout as desired
5. Save your activity

## Media Metadata Requirements

For **best experience with album artwork and rich metadata**:

### Music Files:
- **Format**: MP3, FLAC, OGG, M4A with embedded tags
- **Required Tags**: 
  - Title (song name)
  - Artist (artist name)
  - Album (album name)
  - Album Art (embedded image)
- **Tag Standards**: ID3v2.3/2.4 for MP3, Vorbis comments for FLAC/OGG

### Video Files:
- **Format**: MP4, MKV, AVI with metadata
- **Metadata Fields**: Title, Year, Genre
- **Artwork**: Embedded poster/thumbnail

### Tagging Tools:
- **Windows**: MP3Tag, MusicBrainz Picard
- **macOS**: Kid3, MusicBrainz Picard
- **Linux**: EasyTAG, Kid3, Picard
- **VLC Built-in**: Tools → Media Information → Metadata tab

## Troubleshooting

### Common Issues:

**1. "Connection Failed" Error**
- Verify VLC HTTP interface is enabled
- Check if you can access `http://DEVICE_IP:8080` in browser
- Confirm password matches VLC settings
- Check firewall allows port 8080

**2. "No Metadata Showing"**
- Ensure media files have embedded tags
- Use MP3Tag or similar tool to add metadata
- VLC can only display metadata that exists in files

**3. "No Album Art"**
- Album art must be embedded in media file
- JPG/PNG format recommended
- Verify art shows in VLC player itself first

**4. "Entity Unavailable After Reboot"**
- Integration supports reboot survival
- If issue persists, remove and re-add device

### Debug Information

Enable detailed logging for troubleshooting:

**Docker Environment:**
```bash
# Add to docker-compose.yml environment section
- LOG_LEVEL=DEBUG

# View logs
docker logs uc-intg-vlc
```

**Integration Logs:**
- **Remote Interface**: Settings → Integrations → VLC → View Logs

## For Developers

### Local Development

1. **Clone and setup:**
   ```bash
   git clone https://github.com/mase1981/uc-intg-vlc.git
   cd uc-intg-vlc
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configuration:**
   ```bash
   export UC_CONFIG_HOME=./config
   ```

3. **Run development:**
   ```bash
   python uc_intg_vlc/driver.py
   ```

4. **VS Code debugging:**
   - Open project in VS Code
   - Use F5 to start debugging session
   - Configure integration with real VLC instance

### Project Structure

```
uc-intg-vlc/
├── uc_intg_vlc/              # Main package
│   ├── __init__.py           # Package info  
│   ├── client.py             # VLC HTTP API client
│   ├── config.py             # Configuration management
│   ├── driver.py             # Main integration driver
│   └── media_player.py       # Media player entity
├── .github/workflows/        # GitHub Actions CI/CD
│   └── build.yml             # Automated build pipeline
├── docker-compose.yml        # Docker deployment
├── Dockerfile                # Container build instructions
├── driver.json               # Integration metadata
├── requirements.txt          # Dependencies
├── pyproject.toml            # Python project config
└── README.md                 # This file
```

### Key Implementation Details

#### **VLC HTTP Interface**
- Uses VLC's HTTP JSON API (not telnet)
- Accesses `/requests/status.json` for metadata
- Retrieves album art via `/art` endpoint
- Parses `information.category.meta` for rich metadata

#### **Multi-Device Architecture**
- Each VLC instance = separate client + entity
- Device ID generated from host:port hash
- Independent connection monitoring per device
- Reboot survival through configuration persistence

#### **Metadata Extraction**
```python
# VLC HTTP status.json structure:
{
  "state": "playing",
  "time": 125,
  "length": 245,
  "information": {
    "category": {
      "meta": {
        "title": "Song Name",
        "artist": "Artist Name",
        "album": "Album Name"
      }
    }
  }
}
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and test with real VLC
4. Commit changes: `git commit -m 'Add amazing feature'`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

## Credits

- **Developer**: Meir Miyara
- **VLC**: VideoLAN Organization for VLC Media Player
- **Unfolded Circle**: Remote 2/3 integration framework (ucapi)
- **Community**: Testing and feedback from UC community

## Support & Community

- **GitHub Issues**: [Report bugs and request features](https://github.com/mase1981/uc-intg-vlc/issues)
- **UC Community Forum**: [General discussion and support](https://unfolded.community/)
- **Developer**: [Meir Miyara](https://www.linkedin.com/in/meirmiyara)

---

**Made with ❤️ for the Unfolded Circle Community** 

**Thank You**: Meir Miyara