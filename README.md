# VLC Media Player Integration for Unfolded Circle Remote 2/3

Control your VLC Media Player instances directly from your Unfolded Circle Remote 2 or Remote 3 with **comprehensive media player functionality**, **album artwork**, and **rich metadata display**.

![VLC](https://img.shields.io/badge/VLC-Media%20Player-orange)
[![GitHub Release](https://img.shields.io/github/v/release/mase1981/uc-intg-vlcmedia?style=flat-square)](https://github.com/mase1981/uc-intg-vlcmedia/releases)
![License](https://img.shields.io/badge/license-MPL--2.0-blue?style=flat-square)
[![GitHub issues](https://img.shields.io/github/issues/mase1981/uc-intg-vlcmedia?style=flat-square)](https://github.com/mase1981/uc-intg-vlcmedia/issues)
[![Community Forum](https://img.shields.io/badge/community-forum-blue?style=flat-square)](https://community.unfoldedcircle.com/)
[![Discord](https://badgen.net/discord/online-members/zGVYf58)](https://discord.gg/zGVYf58)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/mase1981/uc-intg-vlcmedia/total?style=flat-square)
[![Buy Me A Coffee](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=flat-square)](https://buymeacoffee.com/meirmiyara)
[![PayPal](https://img.shields.io/badge/PayPal-donate-blue.svg?style=flat-square)](https://paypal.me/mmiyara)
[![Github Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-30363D?&logo=GitHub-Sponsors&logoColor=EA4AAA&style=flat-square)](https://github.com/sponsors/mase1981)


## Features

This integration provides full control of VLC Media Player with rich media information display through the VLC HTTP interface, delivering seamless integration with your Unfolded Circle Remote for complete media playback control.

---
## ❤️ Support Development ❤️

If you find this integration useful, consider supporting development:

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-GitHub-pink?style=for-the-badge&logo=github)](https://github.com/sponsors/mase1981)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/meirmiyara)
[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/mmiyara)

Your support helps maintain this integration. Thank you! ❤️
---

### 🎵 **Media Player Control**

#### **Playback Control**
- **Play/Pause Toggle** - Seamless playback control
- **Previous/Next Track** - Navigate through playlist
- **Fast Forward/Rewind** - 30-second skip controls
- **Seek** - Jump to any position in media
- **Real-time Updates** - Current position tracking

#### **Volume Control**
- **Volume Up/Down** - Adjust volume levels
- **Set Volume** - Direct volume control (0-100)
- **Volume Slider** - Visual volume control
- **Mute Toggle** - Quick mute/unmute
- **Real-time Feedback** - Instant volume updates

### 📺 **Rich Media Information Display**

#### **Dynamic Metadata**
Real-time display of media information from file tags:
- **Media Title** - Song/video title from ID3/metadata tags
- **Artist** - Artist name from file metadata
- **Album** - Album name from file metadata
- **Album Artwork** - High-quality album art via VLC HTTP interface
- **Progress Information** - Current position and total duration
- **Playback State** - Playing, paused, stopped indicators

#### **Multi-Device Support**
- **Multiple VLC Instances** - Control VLC on different devices
- **Individual Configuration** - Separate setup for each VLC player
- **Unique Device Names** - Name each instance (Living Room PC, NVIDIA Shield, etc.)
- **Independent Control** - Each device controlled separately

### **VLC Requirements**

- **Protocol**: VLC HTTP Interface
- **VLC Version**: 3.0.0 or higher
- **HTTP Interface**: Must be enabled in VLC preferences
- **Password**: HTTP interface password required
- **Port**: Default 8080 (configurable)

### **Network Requirements**

- **Local Network Access** - Integration requires same network as VLC
- **HTTP Port** - Default 8080 (configurable)
- **Firewall Configuration** - Ensure VLC HTTP port is accessible
- **Static IP Recommended** - Device should have static IP or DHCP reservation

## Installation

### Option 1: Remote Web Interface (Recommended)
1. Navigate to the [**Releases**](https://github.com/mase1981/uc-intg-vlcmedia/releases) page
2. Download the latest `uc-intg-vlcmedia-<version>-aarch64.tar.gz` file
3. Open your remote's web interface (`http://your-remote-ip`)
4. Go to **Settings** → **Integrations** → **Add Integration**
5. Click **Upload** and select the downloaded `.tar.gz` file

### Option 2: Docker (Advanced Users)

The integration is available as a pre-built Docker image from GitHub Container Registry:

**Image**: `ghcr.io/mase1981/uc-intg-vlcmedia:latest`

**Docker Compose:**
```yaml
services:
  uc-intg-vlcmedia:
    image: ghcr.io/mase1981/uc-intg-vlcmedia:latest
    container_name: uc-intg-vlcmedia
    network_mode: host
    volumes:
      - </local/path>:/config
    environment:
      - UC_CONFIG_HOME=/config
      - UC_INTEGRATION_HTTP_PORT=9090
      - UC_INTEGRATION_INTERFACE=0.0.0.0
      - PYTHONPATH=/app
    restart: unless-stopped
```

**Docker Run:**
```bash
docker run -d --name uc-intg-vlcmedia --restart unless-stopped --network host -v vlcmedia-config:/config -e UC_CONFIG_HOME=/config -e UC_INTEGRATION_INTERFACE=0.0.0.0 -e UC_INTEGRATION_HTTP_PORT=9090 -e PYTHONPATH=/app ghcr.io/mase1981/uc-intg-vlcmedia:latest
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
3. Click **"Configure"** to begin setup:

#### **Device Configuration:**
- **VLC Player IP Address**: IP of device running VLC (e.g., 192.168.1.100)
- **HTTP Port**: VLC HTTP port (default: 8080)
- **Password**: Password you set in VLC Lua HTTP settings
- **Device Name**: Friendly name (e.g., "Living Room PC", "NVIDIA Shield")
- Click **Complete Setup**

#### **Connection Test:**
- Integration verifies VLC HTTP interface accessibility
- Validates password and connection
- Setup fails if device unreachable

4. Integration will create entity:
   - **[Device Name]**: Media player entity for VLC control

## Using the Integration

### Media Player Entity

The media player entity provides comprehensive control:

- **Playback Control**: Play/Pause, Previous, Next, Seek
- **Volume Control**: Volume slider, Up/Down, Mute toggle
- **Media Information**: Title, Artist, Album, Artwork
- **Progress Display**: Current position and total duration
- **Playback State**: Playing, Paused, Stopped indicators

### Media Metadata Requirements

For **best experience with album artwork and rich metadata**:

#### Music Files:
- **Format**: MP3, FLAC, OGG, M4A with embedded tags
- **Required Tags**: Title, Artist, Album, Album Art (embedded image)
- **Tag Standards**: ID3v2.3/2.4 for MP3, Vorbis comments for FLAC/OGG

#### Video Files:
- **Format**: MP4, MKV, AVI with metadata
- **Metadata Fields**: Title, Year, Genre
- **Artwork**: Embedded poster/thumbnail

#### Tagging Tools:
- **Windows**: MP3Tag, MusicBrainz Picard
- **macOS**: Kid3, MusicBrainz Picard
- **Linux**: EasyTAG, Kid3, Picard
- **VLC Built-in**: Tools → Media Information → Metadata tab

## Credits

- **Developer**: Meir Miyara
- **VLC**: VideoLAN Organization for VLC Media Player
- **Unfolded Circle**: Remote 2/3 integration framework (ucapi)
- **Protocol**: VLC HTTP Interface
- **Community**: Testing and feedback from UC community

## License

This project is licensed under the Mozilla Public License 2.0 (MPL-2.0) - see LICENSE file for details.

## Support & Community

- **GitHub Issues**: [Report bugs and request features](https://github.com/mase1981/uc-intg-vlcmedia/issues)
- **UC Community Forum**: [General discussion and support](https://unfolded.community/)
- **Developer**: [Meir Miyara](https://www.linkedin.com/in/meirmiyara)
- **VLC Support**: [Official VLC Support](https://www.videolan.org/support/)

---

**Made with ❤️ for the Unfolded Circle and VLC Communities**

**Thank You**: Meir Miyara
