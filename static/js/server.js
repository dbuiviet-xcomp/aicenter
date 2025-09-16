import express from 'express';
import { spawn, exec } from 'child_process';
import { promises as fs } from 'fs';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(cors());
app.use(express.json());
app.use('/tts/audio', express.static(path.join(__dirname, 'tts', 'audio'))); // Serve audio files

// Ensure tts/audio directory exists
const audioDir = path.join(__dirname, 'tts', 'audio');
fs.mkdir(audioDir, { recursive: true }).catch((error) => {
  console.error('Error creating audio directory:', error);
});

app.post('/tts', async (req, res) => {
  const { text, gender = 'female', area = 'northern', emotion = 'neutral' } = req.body;
  const errorMsgInVNese = 'Lỗi: Không thể kết nối đến máy chủ. Bạn hãy kiểm tra lại các thông số cho chắc chắn và vui lòng thử lại sau.';
  const ttsErrorMsgInVNese = 'Lỗi: Không thể kết nối đến máy chủ, vui lòng thử lại sau.'; // Match App.jsx
  const normalizedText = text.trim();
  const isErrorMessage = normalizedText === errorMsgInVNese || normalizedText === ttsErrorMsgInVNese;
  const ttsText = isErrorMessage ? ttsErrorMsgInVNese : normalizedText;
  const audioFileName = isErrorMessage ? 'error_message.mp3' : `output_${Date.now()}.mp3`;
  const audioFilePath = path.join(audioDir, audioFileName);
  const audioUrl = `http://localhost:3001/tts/audio/${audioFileName}`;

  console.log(`Processing TTS request: text="${normalizedText}", isErrorMessage=${isErrorMessage}`);

  try {
    // Check if error message audio already exists
    if (isErrorMessage) {
      try {
        await fs.access(audioFilePath);
        console.log(`Serving existing audio: ${audioUrl}`);
        return res.json({ audioFile: audioUrl });
      } catch {
        console.log(`Error message audio not found, generating: ${audioFilePath}`);
      }
    }

    // Generate temporary WAV file
    const wavFile = path.join(__dirname, 'tts', `output_${Date.now()}.wav`);

    // Use the virtual environment's Python executable
    const pythonPath = path.join(__dirname, 'tts', 'venv', 'bin', 'python3');

    // Run VietVoice-TTS CLI command
    const pythonProcess = spawn(pythonPath, [
      '-m',
      'vietvoicetts',
      ttsText,
      wavFile,
      '--gender',
      gender,
      '--area',
      area,
      '--emotion',
      emotion,
    ]);

    let errorOutput = '';

    pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    pythonProcess.on('close', async (code) => {
      if (code !== 0) {
        console.error(`VietVoice-TTS error: ${errorOutput}`);
        return res.status(500).json({ error: 'Failed to generate audio', details: errorOutput });
      }

      try {
        // Convert WAV to MP3 using ffmpeg
        await new Promise((resolve, reject) => {
          exec(`ffmpeg -i ${wavFile} -c:a mp3 ${audioFilePath}`, (error) => {
            if (error) {
              reject(error);
            } else {
              resolve();
            }
          });
        });

        // Clean up WAV file
        await fs.unlink(wavFile).catch((error) => {
          console.warn('Error cleaning up WAV file:', error);
        });

        // Clean up non-error MP3 files
        if (!isErrorMessage) {
          setTimeout(async () => {
            await fs.unlink(audioFilePath).catch((error) => {
              console.warn('Error cleaning up MP3 file:', error);
            });
          }, 60000); // Delete after 1 minute
        }

        console.log(`Generated audio: ${audioUrl}`);
        res.json({ audioFile: audioUrl });
      } catch (error) {
        console.error('Error processing audio file:', error);
        res.status(500).json({ error: 'Failed to process audio file' });
      }
    });
  } catch (error) {
    console.error('Server error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Clean up old timestamped files on startup
async function cleanUpOldFiles() {
  try {
    const files = await fs.readdir(audioDir);
    for (const file of files) {
      if (file.startsWith('output_') && file.endsWith('.mp3')) {
        await fs.unlink(path.join(audioDir, file)).catch((error) => {
          console.warn(`Error cleaning up old file ${file}:`, error);
        });
      }
    }
    console.log('Cleaned up old timestamped audio files');
  } catch (error) {
    console.error('Error during cleanup:', error);
  }
}
cleanUpOldFiles();

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`TTS server running on http://localhost:${PORT}`);
});