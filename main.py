import shutil
import atexit
import ctypes
import ctypes.util
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque
import math
import queue
import re
import secrets
import subprocess
import sys
import tempfile
import threading
import time
import unicodedata
from pathlib import Path

import pygame
from pygame._sdl2 import Renderer, Texture, Window


ASSETS = Path(__file__).resolve().parent / "assets"
CLIP_SOURCES = {
    "niceplace.avi": "niceplace.avi",
    "joke_reaction": "niceplace.avi",
    "goodjoke.avi": "goodjoke.avi",
    "joke_keyboard": "lookatthatkeyboard.avi",
    "dontleavemeallalone.avi": "dontleavemeallalone.avi",
    "timeforyoutodie.mp4": "timeforyoutodie.mp4",
    "fly_intro": "flyforyou.avi",
    "fly_loop": "flyforyou.avi",
    "fight_succeeded": "fightsucceeded.mp4",
    "fight_failed": "fightfailed.mp4",
    "ready_to_run": "readytorun.avi",
    "on_your_mark": "onyourmark.avi",
    "goodbye": "okbyebye.avi",
}
CLIP_KEYS = tuple(CLIP_SOURCES)
WIDTH, HEIGHT = 800, 600
VIDEO_SIZE = (800, 560)
VIDEO_FPS = 15
RENDER_FPS = 60
FRAME_BYTES = VIDEO_SIZE[0] * VIDEO_SIZE[1] * 3
QUESTION = "You got a good joke for Mario?"
SCALE_PAD = (
    "scale=800:560:force_original_aspect_ratio=decrease:flags=fast_bilinear,"
    "pad=800:560:(ow-iw)/2:(oh-ih)/2:black"
)
VIDEO_FILTERS = {
    "niceplace.avi": f"{SCALE_PAD},fps={VIDEO_FPS}",
    "joke_reaction": f"fps={VIDEO_FPS},trim=end=1.15,setpts=PTS-STARTPTS,{SCALE_PAD}",
    "goodjoke.avi": f"{SCALE_PAD},fps={VIDEO_FPS}",
    "joke_keyboard": f"{SCALE_PAD},fps={VIDEO_FPS}",
    "dontleavemeallalone.avi": f"{SCALE_PAD},fps={VIDEO_FPS}",
    "timeforyoutodie.mp4": f"{SCALE_PAD},fps={VIDEO_FPS}",
    "fly_intro": f"fps={VIDEO_FPS},trim=end=2,setpts=PTS-STARTPTS,{SCALE_PAD}",
    "fly_loop": (
        f"fps={VIDEO_FPS},trim=start=2:end=11.5,setpts=PTS-STARTPTS,"
        f"loop=loop=-1:size=143:start=0,{SCALE_PAD}"
    ),
    "fight_succeeded": f"{SCALE_PAD},fps={VIDEO_FPS}",
    "fight_failed": f"{SCALE_PAD},fps={VIDEO_FPS}",
    "ready_to_run": f"{SCALE_PAD},fps={VIDEO_FPS}",
    "on_your_mark": f"{SCALE_PAD},fps={VIDEO_FPS}",
    "goodbye": f"{SCALE_PAD},fps={VIDEO_FPS}",
}
AUDIO_SEGMENTS = {
    "joke_reaction": (0, 1.15),
    "fly_intro": (0, 2),
    "fly_loop": (2, 9.5),
}
TWEEN_SECONDS = 0.75
FLY_PAUSE_SECONDS = 2.0
LOSS_BOUNCE_SECONDS = 7.5
LOSS_MUSIC_START_SPEED = 1.75
BOUNCE_CROSSING_FRAMES = 4
BORDER_BOUNCES_BEFORE_FIGHT = 50
IKEMEN_DIR = ASSETS / "ikemengo"
CHASE_SECONDS = 30.0
CHASE_SPEED = 1650.0
INFO_SOUND_CANDIDATES = {
    "linux": (
        Path("/usr/share/sounds/freedesktop/stereo/message.oga"),
        Path("/usr/share/sounds/freedesktop/stereo/dialog-information.oga"),
        Path("/usr/share/sounds/freedesktop/stereo/complete.oga"),
        Path("/usr/share/sounds/ubuntu/stereo/dialog-information.ogg"),
    ),
    "darwin": (
        Path("/System/Library/Sounds/Glass.aiff"),
        Path("/System/Library/Sounds/Hero.aiff"),
    ),
}
ERROR_SOUND_CANDIDATES = {
    "linux": (
        Path("/usr/share/sounds/Oxygen-Sys-App-Error-Critical.ogg"),
        Path("/usr/share/sounds/freedesktop/stereo/dialog-error.oga"),
        Path("/usr/share/sounds/freedesktop/stereo/dialog-error.ogg"),
        Path("/usr/share/sounds/ubuntu/stereo/dialog-error.ogg"),
    ),
    "darwin": (
        Path("/System/Library/Sounds/Basso.aiff"),
        Path("/System/Library/Sounds/Sosumi.aiff"),
    ),
}


def ikemen_executable() -> Path:
    if sys.platform.startswith("linux"):
        name = "Ikemen_GO_Linux"
    elif sys.platform == "darwin":
        name = "Ikemen_GO.command"
    elif sys.platform == "win32":
        name = "Ikemen_GO.exe"
    else:
        raise RuntimeError(f"IKEMEN GO is not configured for {sys.platform}.")
    return IKEMEN_DIR / name


def _install_terminal_restore():
    if not sys.stdin.isatty():
        return None
    try:
        import termios

        fd = sys.stdin.fileno()
        original = termios.tcgetattr(fd)
    except (ImportError, OSError, ValueError):
        return None

    def restore() -> None:
        try:
            termios.tcsetattr(fd, termios.TCSANOW, original)
        except (OSError, ValueError):
            pass

    atexit.register(restore)
    return restore


FEATURE_COUNT = 14
MODEL_PATH = Path(__file__).resolve().parent / "assets" / "jokeeval.onnx"
JOKE_NOUNS = (
    "penguin", "duck", "fish", "frog", "cat", "dog", "elephant", "bear",
    "rabbit", "mouse", "owl", "bee", "cow", "pig", "horse", "turtle",
    "snake", "shark", "monkey", "squirrel", "robot", "pirate", "astronaut",
    "teacher", "doctor", "baker", "chef", "ghost", "vampire", "snowman",
    "banana", "potato", "pizza", "sandwich", "shoe", "umbrella", "phone",
    "clock", "book", "lamp", "fridge", "spoon", "suitcase", "mailbox",
    "door", "cloud", "moon", "volcano", "bicycle", "calendar", "computer",
    "scarecrow", "tomato", "pencil",
)
CONNECTIVES = {
    "although", "because", "but", "except", "however", "instead", "since",
    "so", "therefore", "then", "though", "until", "when", "while",
    "ademas", "aunque", "asi", "como", "cuando", "despues", "entonces",
    "pero", "porque", "por", "pues", "sin", "tambien", "entretanto",
    "mas", "portanto", "quando", "tambem", "todavia", "contudo",
}
HUMOR_CUES = {
    "absurd", "banana", "because", "chicken", "cross", "dad", "funny",
    "joke", "knock", "laugh", "pun", "road", "side", "why", "what", "how",
    "broma", "chiste", "gracioso", "risa", "pollo", "gallina", "cruzar",
    "camino", "carretera", "piada", "engracado", "rir", "galinha", "frango",
    "atravessar", "estrada", "por", "que", "como", "qual", "quien", "quem",
    "abeja", "zum", "techo", "vaca", "concentrada", "matematicas", "problema",
    "libro", "pato", "huevo", "zero", "cinto", "tomate", "extrato", "pato",
    "queijo", "piao", "banco", "pave", "piada",
    "penguin", "penguins", "pinguino", "pingüino", "duck", "fish", "frog",
    "cat", "dog", "elephant", "bear", "rabbit", "mouse", "owl", "bee",
    "cow", "pig", "horse", "turtle", "snake", "shark", "monkey", "squirrel",
    "robot", "pirate", "astronaut", "teacher", "doctor", "baker", "chef",
    "ghost", "vampire", "snowman", "potato", "pizza", "sandwich", "shoe",
    "umbrella", "phone", "clock", "book", "lamp", "fridge", "spoon", "suitcase",
    "mailbox", "door", "cloud", "moon", "volcano", "ice", "cold", "waddle",
    "beak", "flight", "fly", "chilly", "pato", "peixe", "sapo", "gato", "cachorro",
    "elefante", "urso", "coelho", "rato", "coruja", "porco", "cavalo", "tartaruga",
    "cobra", "tubarao", "macaco", "pingüim", "pingui", "pinguino", "pato", "pez",
    "rana", "perro", "oso", "conejo", "raton", "buho", "cerdo", "caballo", "tortuga",
    "serpiente", "tiburon", "mono", "hielo", "frio", "pico", "volar", "pinguim",
}
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by",
    "for", "from", "he", "her", "his", "i", "in", "is", "it", "its",
    "of", "on", "or", "our", "she", "so", "that", "the", "their",
    "they", "this", "to", "was", "we", "were", "with", "you", "your",
    "al", "algo", "como", "con", "de", "del", "el", "ella", "ellas",
    "ellos", "en", "es", "esta", "este", "la", "las", "lo", "los", "me",
    "mi", "muy", "no", "nos", "o", "para", "por", "que", "se", "ser",
    "si", "su", "sus", "un", "una", "unos", "unas", "y", "yo",
    "ainda", "as", "com", "da", "das", "do", "dos", "e", "ela", "elas",
    "ele", "eles", "em", "eu", "foi", "mais", "na", "nas", "nem", "no",
    "nos", "os", "ou", "pelo", "pela", "pelos", "pelas", "seu", "sua",
    "um", "uma", "voce", "voces",
}
_MODEL_LOCK = threading.Lock()
_LOADED_SESSION_KEY: tuple[str, int, int] | None = None
_LOADED_SESSION = None

def _normalized_word(word: str) -> str:
    decomposed = unicodedata.normalize("NFD", word.casefold())
    return "".join(character for character in decomposed
                   if unicodedata.category(character) != "Mn")


def extract_features(text: str) -> list[float]:
    words = re.findall(r"[^\W\d_]+(?:['’][^\W\d_]+)*", text, flags=re.UNICODE)
    lowered = [_normalized_word(word) for word in words]
    count = len(words)
    unique = set(lowered)
    sentences = [part for part in re.split(r"[.!?]+", text) if part.strip()]
    content = [word for word in lowered if word not in STOP_WORDS]
    content_unique = set(content)
    repetition = (count - len(unique)) / max(1, count)
    adjacent_repeat = sum(a == b for a, b in zip(lowered, lowered[1:])) / max(1, count - 1)
    connectors = sum(word in CONNECTIVES for word in lowered)
    humor = sum(word in HUMOR_CUES for word in lowered)
    grammar = 0.0
    if count:
        grammar = (
            0.2 * float(text.lstrip()[:1].isupper())
            + 0.2 * float(text.rstrip().endswith((".", "!", "?")))
            + 0.2 * float(text.count("(") == text.count(")"))
            + 0.2 * float(text.count('"') % 2 == 0)
            + 0.2 * float(not any(pattern in " " + " ".join(lowered) + " " for pattern in (
                " i is ", " they is ", " we was ", " he are ", " she are ",
                " a apple ", " an banana ", " yo es ", " ellos es ", " nosotros fue ",
                " el manzana ", " la problema ", " eles e ", " nos foi ", " eu esta ",
                " um banana ", " uma problema ",
            )))
        )
    if len(sentences) < 2:
        cohesion = 0.65 if count else 0.0
    else:
        sentence_words = [
            {_normalized_word(word) for word in re.findall(
                r"[^\W\d_]+(?:['’][^\W\d_]+)*", sentence, flags=re.UNICODE
            ) if _normalized_word(word) not in STOP_WORDS}
            for sentence in sentences
        ]
        overlap = []
        for left, right in zip(sentence_words, sentence_words[1:]):
            overlap.append(len(left & right) / max(1, len(left | right)))
        cohesion = min(1.0, 0.35 + 0.55 * (sum(overlap) / max(1, len(overlap)))
                       + 0.1 * min(1.0, connectors / 2))
    setup = float(
        ("?" in text or "¿" in text)
        and any(word in lowered for word in (
            "why", "what", "how", "que", "como", "cual", "quien", "quem",
            "qual", "porque",
        ))
    )
    return [
        min(1.0, len(text) / 240),
        min(1.0, count / 40),
        min(1.0, (sum(map(len, words)) / max(1, count)) / 10),
        min(1.0, len(sentences) / 5),
        len(unique) / max(1, count),
        repetition,
        min(1.0, connectors / 4),
        grammar,
        cohesion,
        min(1.0, humor / 3),
        setup,
        float(bool(count) and text.rstrip().endswith((".", "!", "?"))),
        float(bool(count) and text.lstrip()[:1].isupper()),
        adjacent_repeat,
    ]


def _load_session(model_path: Path):
    global _LOADED_SESSION_KEY, _LOADED_SESSION
    try:
        import numpy as np
        import onnxruntime as ort
    except ImportError as exc:
        raise RuntimeError("Install the onnxruntime CPU package to rate jokes.") from exc
    try:
        resolved = model_path.resolve()
        metadata = resolved.stat()
    except OSError:
        return None
    cache_key = (str(resolved), metadata.st_mtime_ns, metadata.st_size)
    with _MODEL_LOCK:
        if _LOADED_SESSION_KEY == cache_key and _LOADED_SESSION is not None:
            return _LOADED_SESSION
        options = ort.SessionOptions()
        options.intra_op_num_threads = 1
        options.inter_op_num_threads = 1
        options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        session = ort.InferenceSession(
            str(resolved), sess_options=options, providers=["CPUExecutionProvider"]
        )
        session.run(None, {"features": np.zeros((1, FEATURE_COUNT), dtype=np.float32)})
        _LOADED_SESSION = session
        _LOADED_SESSION_KEY = cache_key
        return session


def preload_model(model_path: Path = MODEL_PATH) -> bool:
    return _load_session(model_path) is not None


def score_text(text: str, model_path: Path = MODEL_PATH) -> int:
    words = re.findall(r"[^\W\d_]+(?:['’][^\W\d_]+)*", text, flags=re.UNICODE)
    normalized = [_normalized_word(word) for word in words]
    content_words = {word for word in normalized if word not in STOP_WORDS}
    if len(words) < 4 or len(content_words) < 4:
        return 5

    import numpy as np

    session = _load_session(model_path)
    if session is None:
        return 5
    features = np.asarray([extract_features(text)], dtype=np.float32)
    score = float(session.run(None, {"features": features})[0].reshape(-1)[0])
    return max(0, min(10, int(round(score))))




class RateControlledMusic:
    """Loop decoded PCM with OpenAL so changing AL_PITCH changes rate and pitch."""

    AL_FORMAT_STEREO16 = 0x1103
    AL_BUFFER = 0x1009
    AL_LOOPING = 0x1007
    AL_PITCH = 0x1003
    AL_SEC_OFFSET = 0x1024

    def __init__(self, ffmpeg: str, song: Path, start_seconds: float) -> None:
        library = ctypes.util.find_library("openal")
        if library is None:
            raise RuntimeError("OpenAL is unavailable")
        self.lib = ctypes.CDLL(library)
        self.lib.alcOpenDevice.argtypes = [ctypes.c_char_p]
        self.lib.alcOpenDevice.restype = ctypes.c_void_p
        self.lib.alcCreateContext.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.lib.alcCreateContext.restype = ctypes.c_void_p
        self.lib.alcMakeContextCurrent.argtypes = [ctypes.c_void_p]
        self.lib.alcMakeContextCurrent.restype = ctypes.c_ubyte
        self.lib.alcDestroyContext.argtypes = [ctypes.c_void_p]
        self.lib.alcCloseDevice.argtypes = [ctypes.c_void_p]
        self.lib.alGenBuffers.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_uint)]
        self.lib.alBufferData.argtypes = [
            ctypes.c_uint, ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int
        ]
        self.lib.alGenSources.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_uint)]
        self.lib.alSourcei.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.c_int]
        self.lib.alSourcef.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.c_float]
        self.lib.alSourcePlay.argtypes = [ctypes.c_uint]
        self.lib.alSourceStop.argtypes = [ctypes.c_uint]
        self.lib.alDeleteSources.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_uint)]
        self.lib.alDeleteBuffers.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_uint)]

        decoded = subprocess.run(
            [ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(song),
             "-vn", "-f", "s16le", "-acodec", "pcm_s16le", "-ac", "2",
             "-ar", "44100", "pipe:1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        if not decoded.stdout:
            raise RuntimeError("FFmpeg decoded no audio for vspatrick.mp3")
        self.pcm = ctypes.create_string_buffer(decoded.stdout)
        self.device = self.lib.alcOpenDevice(None)
        if not self.device:
            raise RuntimeError("OpenAL could not open the system audio device")
        self.context = self.lib.alcCreateContext(self.device, None)
        if not self.context or not self.lib.alcMakeContextCurrent(self.context):
            self.lib.alcCloseDevice(self.device)
            raise RuntimeError("OpenAL could not create an audio context")
        self.buffer = ctypes.c_uint()
        self.source = ctypes.c_uint()
        self.lib.alGenBuffers(1, ctypes.byref(self.buffer))
        self.lib.alBufferData(
            self.buffer, self.AL_FORMAT_STEREO16, self.pcm, len(decoded.stdout), 44_100
        )
        self.lib.alGenSources(1, ctypes.byref(self.source))
        self.lib.alSourcei(self.source, self.AL_BUFFER, self.buffer.value)
        self.lib.alSourcei(self.source, self.AL_LOOPING, 1)
        self.lib.alSourcef(self.source, self.AL_SEC_OFFSET, max(0.0, start_seconds))

    def play(self, rate: float) -> None:
        self.set_rate(rate)
        self.lib.alSourcePlay(self.source)

    def set_rate(self, rate: float) -> None:
        self.lib.alSourcef(self.source, self.AL_PITCH, ctypes.c_float(rate))

    def close(self) -> None:
        if self.source.value:
            self.lib.alSourceStop(self.source)
            self.lib.alDeleteSources(1, ctypes.byref(self.source))
            self.source = ctypes.c_uint()
        if self.buffer.value:
            self.lib.alDeleteBuffers(1, ctypes.byref(self.buffer))
            self.buffer = ctypes.c_uint()
        self.lib.alcMakeContextCurrent(None)
        if self.context:
            self.lib.alcDestroyContext(self.context)
            self.context = None
        if self.device:
            self.lib.alcCloseDevice(self.device)
            self.device = None


class MarioHead:
    def __init__(self, skip_to: str | None = None) -> None:
        pygame.init()
        self.sdl = self._load_sdl_for_global_mouse()
        self.window = Window("Mario Head", size=(WIDTH, HEIGHT), resizable=True)
        self._set_window_always_on_top(self.window, True)
        try:
            self.renderer = Renderer(self.window, accelerated=False)
        except Exception as exc:
            self.window.destroy()
            raise RuntimeError(f"SDL could not create a software renderer: {exc!r}") from exc
        self.canvas = pygame.Surface((WIDTH, HEIGHT))
        self.canvas_texture = Texture(self.renderer, (WIDTH, HEIGHT), streaming=True)
        self.canvas_dirty = True
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 30)
        self.ffmpeg = shutil.which("ffmpeg")
        self.temp_dir = tempfile.TemporaryDirectory(prefix="mario-head-")
        self.sounds: dict[str, pygame.mixer.Sound | None] = {}
        self.critical_sound: pygame.mixer.Sound | None = None
        self.decoders: dict[str, subprocess.Popen] = {}
        self.audio_channel: pygame.mixer.Channel | None = None
        self.catch_sound_channel: pygame.mixer.Channel | None = None
        self.alarm_channel: pygame.mixer.Channel | None = None
        self.catch_sound: pygame.mixer.Sound | None = None
        self.alarm_sound: pygame.mixer.Sound | None = None
        self.alarm_active = False
        self.current_decoder: subprocess.Popen | None = None
        self.frame_queue: queue.Queue[bytes | None] | None = None
        self.frame_reader_thread: threading.Thread | None = None
        self.frame_reader_stop: threading.Event | None = None
        self.current_clip: str | None = None
        self.finish_callback = None
        self.video_ended = False
        self.frame: pygame.Surface | None = None
        self.scaled_frame: pygame.Surface | None = None
        self.scaled_frame_size: tuple[int, int] | None = None
        self.clip_started_at = 0.0
        self.video_frames_consumed = 0
        self.question_open = False
        self.question_started = 0.0
        self.wait_clip_started = False
        self.question_tk = None
        self.question_root = None
        self.question_window = None
        self.qt_app = None
        self.joke_window = None
        self.joke_pending_text: str | None = None
        self.joke_close_requested = False
        self.joke_input_open = False
        self.joke_ready = False
        self.joke_video_done = False
        self.joke_future = None
        self.joke_result_deadline: float | None = None
        self.joke_result_won = False
        self.joke_executor: ThreadPoolExecutor | None = None
        self.joke_warm_future = None
        self.skip_star_down = False
        self.skip_minus_down = False
        self.skip_chord_latched = False
        self.resize_tween: dict | None = None
        self.bouncing = False
        self.window_x = 0.0
        self.window_y = 0.0
        self.velocity_x = 650.0
        self.velocity_y = 500.0
        self.desktop_width, self.desktop_height = self._desktop_size()
        self.home_size = tuple(self.window.size)
        self.window_x = max(0, (self.desktop_width - WIDTH) // 2)
        self.window_y = max(0, (self.desktop_height - HEIGHT) // 2)
        self.window.position = (self.window_x, self.window_y)
        self.home_position = (self.window_x, self.window_y)
        self.home_center = (self.window_x + self.home_size[0] / 2,
                            self.window_y + self.home_size[1] / 2)
        self.bounce_count = 0
        self.launch_ikemen = False
        self.loss_bouncing = False
        self.loss_reaction_pending = False
        self.loss_bounce_started = 0.0
        self.loss_bounce_count = 0
        self.loss_speed_scale = 3.0
        self.loss_music_speed = LOSS_MUSIC_START_SPEED
        self.result_pending = False
        self.loss_music: RateControlledMusic | None = None
        self.chasing = False
        self.chase_started = 0.0
        self.chase_texture_frame: pygame.Surface | None = None
        self.chase_music_active = False
        self.chase_escape_until = 0.0
        self.chase_escape_velocity = (0.0, 0.0)
        self.chase_timer_window: Window | None = None
        self.chase_timer_renderer: Renderer | None = None
        self.chase_timer_texture: Texture | None = None
        self.chase_timer_font = pygame.font.Font(None, 80)
        self.chase_timer_value: int | None = None
        self.chase_timer_target_size: tuple[int, int] | None = None
        self.chase_timer_tween: dict | None = None
        self.chase_timer_dismiss_tween: dict | None = None
        self.chase_timer_color: tuple[int, int, int] | None = None
        self.chase_timer_dirty = False
        self.chase_positions = deque(maxlen=10)
        self.chase_last_sample = None
        self.chase_entropy = secrets.SystemRandom()
        self.exit_after_sound = False
        self.resources_closed = False
        self.song_duration = 0.0
        self.song_position_at_fight = 0.0
        self.running = True

        if self.ffmpeg is None:
            raise RuntimeError("ffmpeg is required to play the video files.")

        try:
            pygame.mixer.init(frequency=44_100, size=-16, channels=2, buffer=1024)
            self.audio_channel = pygame.mixer.Channel(0)
            self.catch_sound_channel = pygame.mixer.Channel(1)
            self.alarm_channel = pygame.mixer.Channel(2)
            self.critical_sound = self._load_critical_sound()
        except pygame.error:
            self.audio_channel = None
            self.catch_sound_channel = None
            self.alarm_channel = None

        self._prepare_clips()
        if skip_to is None and (ASSETS / "jokeeval.onnx").is_file():
            self.joke_executor = ThreadPoolExecutor(
                max_workers=1, thread_name_prefix="mario-joke-eval"
            )
            self.joke_warm_future = self.joke_executor.submit(
                self._preload_joke_model
            )
        if skip_to in ("lose", "win"):
            self._show_fight_result(skip_to == "win")
        else:
            self._start_clip("niceplace.avi", self._start_good_joke)

    def _draw_preparing(self, text: str) -> None:
        self.canvas.fill((0, 0, 0))
        label = self.font.render(text, True, (235, 235, 235))
        self.canvas.blit(label, label.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        self.canvas_dirty = True
        self._present()

    def _present(self) -> None:
        if self.canvas_dirty:
            self.canvas_texture.update(self.canvas)
            self.canvas_dirty = False
        self.renderer.draw_color = (0, 0, 0, 255)
        self.renderer.clear()
        width, height = self.window.size
        self.canvas_texture.draw(dstrect=(0, 0, width, height))
        self.renderer.present()

    def _desktop_size(self) -> tuple[int, int]:
        sizes = pygame.display.get_desktop_sizes()
        display_index = min(self.window.display_index, len(sizes) - 1)
        return sizes[display_index]

    @staticmethod
    def _load_sdl_for_global_mouse():
        for library_name in ("SDL2-2.0", "SDL2"):
            library_path = ctypes.util.find_library(library_name)
            if library_path:
                try:
                    library = ctypes.CDLL(library_path)
                    library.SDL_GetGlobalMouseState.argtypes = [
                        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)
                    ]
                    library.SDL_GetGlobalMouseState.restype = ctypes.c_uint
                    return library
                except (AttributeError, OSError):
                    continue
        return None

    def _extract_chase_frame(self) -> bytes:
        source = ASSETS / "flyforyou.avi"
        result = subprocess.run(
            [self.ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(source),
             "-vf", f"select=eq(n\\,29),{SCALE_PAD}", "-vsync", "0",
             "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        if len(result.stdout) != FRAME_BYTES:
            raise RuntimeError("Could not extract frame 30 from assets/flyforyou.avi")
        return result.stdout

    def _prepare_clips(self) -> None:
        """Prepare each unique video source concurrently, one worker per file."""
        source_keys: dict[str, list[str]] = {}
        for key in CLIP_KEYS:
            source = str((ASSETS / CLIP_SOURCES[key]).resolve())
            source_keys.setdefault(source, []).append(key)

        futures = {}
        with ThreadPoolExecutor(max_workers=max(1, len(source_keys))) as pool:
            for source, keys in source_keys.items():
                futures[pool.submit(self._prepare_source, Path(source), keys)] = source
            completed = 0
            for future in as_completed(futures):
                result = future.result()
                completed += 1
                self._draw_preparing(
                    f"Preparing videos {completed} of {len(source_keys)}…"
                )
                for key, decoder in result["decoders"].items():
                    self.decoders[key] = decoder
                for key, wav_path in result["audio"].items():
                    if wav_path is not None and self.audio_channel is not None:
                        try:
                            self.sounds[key] = pygame.mixer.Sound(str(wav_path))
                        except pygame.error:
                            self.sounds[key] = None
                    else:
                        self.sounds[key] = None
                if "fly_loop" in result["audio"]:
                    self.sounds["chase_fly"] = self.sounds.get("fly_loop")
                if result["chase_frame"] is not None:
                    self.chase_texture_frame = pygame.image.frombuffer(
                        result["chase_frame"], VIDEO_SIZE, "RGB"
                    ).copy()

    def _prepare_source(self, source: Path, keys: list[str]) -> dict:
        if not source.is_file():
            raise FileNotFoundError(f"Video file not found: {source}")
        decoders = {}
        audio_paths = {}
        audio_cache = {}
        for key in keys:
            decoders[key] = self._launch_decoder(key)
        for key in keys:
            segment = AUDIO_SEGMENTS.get(key)
            if segment not in audio_cache:
                wav_path = Path(self.temp_dir.name) / (
                    f"audio-{source.stem}-{segment[0]}-{segment[1]}.wav"
                    if segment else f"audio-{source.stem}-full.wav"
                )
                audio_args = [self.ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                              "-i", str(source), "-vn"]
                if segment is not None:
                    audio_args.extend(["-ss", str(segment[0]), "-t", str(segment[1])])
                audio_args.extend(["-ac", "2", "-ar", "44100", "-c:a", "pcm_s16le",
                                   str(wav_path)])
                result = subprocess.run(
                    audio_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                audio_cache[segment] = (
                    wav_path if result.returncode == 0 and wav_path.is_file() else None
                )
            audio_paths[key] = audio_cache[segment]

        chase_frame = None
        if source.name == "flyforyou.avi":
            chase_frame = self._extract_chase_frame()

        return {"decoders": decoders, "audio": audio_paths,
                "chase_frame": chase_frame}

    @staticmethod
    def _load_critical_sound() -> pygame.mixer.Sound | None:
        candidates = ERROR_SOUND_CANDIDATES.get(sys.platform, ())
        for path in candidates:
            if path.is_file():
                try:
                    return pygame.mixer.Sound(str(path))
                except pygame.error:
                    continue
        return None

    def _play_critical_sound(self) -> None:
        if self.critical_sound is not None:
            self.critical_sound.play()
            return
        if sys.platform == "win32":
            try:
                import winsound
                winsound.PlaySound(
                    "SystemHand", winsound.SND_ALIAS | winsound.SND_ASYNC
                )
            except (ImportError, RuntimeError):
                try:
                    winsound.MessageBeep(winsound.MB_ICONHAND)
                except (NameError, RuntimeError):
                    pass
        elif sys.platform == "darwin":
            sound_path = next(
                (path for path in ERROR_SOUND_CANDIDATES["darwin"] if path.is_file()),
                None,
            )
            player = shutil.which("afplay")
            if sound_path is not None and player is not None:
                try:
                    subprocess.Popen(
                        [player, str(sound_path)],
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                except OSError:
                    pass

    def _launch_decoder(self, key: str) -> subprocess.Popen:
        source = ASSETS / CLIP_SOURCES[key]
        return subprocess.Popen(
            [self.ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(source),
             "-an", "-vf", VIDEO_FILTERS[key], "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=0,
        )

    @staticmethod
    def _read_frame(pipe) -> bytes:
        data = bytearray(FRAME_BYTES)
        view = memoryview(data)
        offset = 0
        while offset < FRAME_BYTES:
            count = pipe.readinto(view[offset:])
            if not count:
                break
            offset += count
        return bytes(data) if offset == FRAME_BYTES else bytes(view[:offset])

    def _stop_current(self) -> None:
        if self.audio_channel is not None:
            self.audio_channel.stop()
        if self.frame_reader_stop is not None:
            self.frame_reader_stop.set()
        process, self.current_decoder = self.current_decoder, None
        if process is not None:
            if process.poll() is None:
                process.terminate()
            if process.stdout is not None:
                process.stdout.close()
            process.wait()
        reader, self.frame_reader_thread = self.frame_reader_thread, None
        if reader is not None and reader is not threading.current_thread():
            reader.join(timeout=0.25)
        self.frame_queue = None
        self.frame_reader_stop = None

    def _start_clip(self, key: str, on_finish=None, *, loops: int = 0) -> None:
        self._stop_current()
        decoder = self.decoders.pop(key, None)
        if decoder is None:
            decoder = self._launch_decoder(key)
        self.current_clip = key
        self.current_decoder = decoder
        self.frame_queue = queue.Queue(maxsize=2)
        self.frame_reader_stop = threading.Event()
        self.frame_reader_thread = threading.Thread(
            target=self._read_frames,
            args=(decoder.stdout, self.frame_queue, self.frame_reader_stop),
            daemon=True,
        )
        self.frame_reader_thread.start()
        self.finish_callback = on_finish
        self.video_ended = False
        self.clip_started_at = time.monotonic()
        self.video_frames_consumed = 0
        self.scaled_frame = None
        sound = self.sounds.get(key)
        if self.audio_channel is not None and sound is not None:
            self.audio_channel.play(sound, loops=loops)
            self.clip_started_at = time.monotonic()

    def _read_frames(self, pipe, frames: queue.Queue[bytes | None],
                     stop: threading.Event) -> None:
        if pipe is None:
            if not stop.is_set():
                frames.put(None)
            return
        try:
            while not stop.is_set():
                data = self._read_frame(pipe)
                if len(data) != FRAME_BYTES:
                    break
                while not stop.is_set():
                    try:
                        frames.put(data, timeout=0.1)
                        break
                    except queue.Full:
                        continue
        except (OSError, ValueError):
            pass
        finally:
            while not stop.is_set():
                try:
                    frames.put(None, timeout=0.1)
                    break
                except queue.Full:
                    continue

    def _start_good_joke(self) -> None:
        self._start_clip("goodjoke.avi", self._ask_question)

    def _ask_question(self) -> None:
        self.question_open = True
        self.question_started = time.monotonic()
        self.wait_clip_started = False
        import tkinter as tk

        if self.question_root is None:
            self.question_tk = tk
            self.question_root = tk.Tk()
            self.question_root.withdraw()
        dialog = tk.Toplevel(self.question_root)
        self.question_window = dialog
        dialog.title("Hey!")
        dialog.resizable(False, False)
        dialog.protocol("WM_DELETE_WINDOW", lambda: self._answer(False))
        frame = tk.Frame(dialog, padx=22, pady=18)
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text=QUESTION, padx=12, pady=8).pack()
        buttons = tk.Frame(frame)
        buttons.pack(pady=(12, 0))
        tk.Button(buttons, text="Yes", width=10,
                  command=lambda: self._answer(True)).pack(side="left", padx=6)
        tk.Button(buttons, text="No", width=10,
                  command=lambda: self._answer(False)).pack(side="left", padx=6)
        dialog.update_idletasks()
        width, height = dialog.winfo_reqwidth(), dialog.winfo_reqheight()
        x = (dialog.winfo_screenwidth() - width) // 2
        y = (dialog.winfo_screenheight() - height) // 2
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.lift()

    def _answer(self, yes: bool) -> None:
        if not self.question_open:
            return
        self.question_open = False
        dialog, self.question_window = self.question_window, None
        if dialog is not None:
            try:
                dialog.destroy()
            except self.question_tk.TclError:
                pass
        if yes:
            self._begin_joke_entry()
        else:
            self._start_clip("timeforyoutodie.mp4", self._begin_fly_video)

    def _begin_joke_entry(self) -> None:
        self.result_pending = True
        self._stop_current()
        self.current_clip = None
        self.finish_callback = None
        self.video_ended = False
        self.joke_input_open = True
        self.joke_ready = False
        self.joke_video_done = False
        self.desktop_width, self.desktop_height = self._desktop_size()
        self._create_joke_window()
        target_size = (max(1, self.home_size[0] // 2), max(1, self.home_size[1] // 2))
        target_center = (target_size[0] / 2, self.desktop_height / 2)
        self.resize_tween = {
            "started": time.monotonic(),
            "from": tuple(self.window.size),
            "to": target_size,
            "from_center": (self.window_x + self.window.size[0] / 2,
                            self.window_y + self.window.size[1] / 2),
            "to_center": target_center,
            "purpose": "joke_position",
        }

    def _create_joke_window(self) -> None:
        try:
            from PySide6.QtCore import Qt, QSignalBlocker, QTimer
            from PySide6.QtWidgets import (
                QApplication, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget,
            )
        except ImportError as exc:
            raise RuntimeError(
                "PySide6 is required for the joke input window."
            ) from exc

        if self.qt_app is None:
            self.qt_app = QApplication.instance() or QApplication([])
            self.qt_app.setQuitOnLastWindowClosed(False)
        mario = self

        class JokeInputWindow(QWidget):
            def __init__(self) -> None:
                super().__init__()
                self.submitted = False
                self.owner_closing = False
                self.close_notified = False
                self.setWindowTitle("It's time for you to type!")
                self.setFixedSize(500, 420)
                self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
                layout = QVBoxLayout(self)
                self.editor = QPlainTextEdit(self)
                self.editor.setPlaceholderText("Gimme a joke!")
                self.editor.setMaximumBlockCount(100)
                self.button = QPushButton("Tell Mario!", self)
                self.button.setEnabled(False)
                self.editor.textChanged.connect(self._text_changed)
                self.button.clicked.connect(self._submit)
                layout.addWidget(self.editor, 1)
                layout.addWidget(self.button)

            def _text_changed(self) -> None:
                text = self.editor.toPlainText()
                if len(text) > 2000:
                    cursor_position = min(self.editor.textCursor().position(), 2000)
                    blocker = QSignalBlocker(self.editor)
                    self.editor.setPlainText(text[:2000])
                    del blocker
                    cursor = self.editor.textCursor()
                    cursor.setPosition(cursor_position)
                    self.editor.setTextCursor(cursor)
                self.button.setEnabled(bool(self.editor.toPlainText().strip()))

            def _submit(self) -> None:
                joke = self.editor.toPlainText().strip()
                if not joke:
                    return
                self.submitted = True
                self.close()
                mario._joke_submitted(joke)

            def closeEvent(self, event) -> None:
                if not self.submitted and not self.owner_closing and not self.close_notified:
                    self.close_notified = True
                    QTimer.singleShot(0, mario._joke_window_closed)
                event.accept()

        size = (500, 420)
        self.joke_window = JokeInputWindow()
        screen = self.qt_app.primaryScreen()
        if screen is not None:
            bounds = screen.availableGeometry()
            self.joke_window.move(
                bounds.right() - size[0] + 1,
                bounds.top() + (bounds.height() - size[1]) // 2,
            )
        self.joke_window.show()
        self.joke_window.raise_()
        self.joke_window.activateWindow()
        self.joke_window.editor.setFocus()

    def _pump_qt_events(self) -> None:
        if self.qt_app is not None:
            self.qt_app.processEvents()
        if self.question_root is not None:
            try:
                self.question_root.update()
            except self.question_tk.TclError:
                self.question_root = None
                self.question_window = None
                self.question_open = False

    def _destroy_joke_window(self) -> None:
        window, self.joke_window = self.joke_window, None
        if window is not None:
            window.owner_closing = True
            window.close()
        self.joke_input_open = False

    def _joke_submitted(self, joke: str) -> None:
        if not self.joke_input_open:
            return
        self.joke_pending_text = joke.strip()
        self.joke_close_requested = False
        self._prepare_joke_return()

    def _joke_window_closed(self) -> None:
        if not self.joke_input_open:
            return
        self.joke_pending_text = None
        self.joke_close_requested = True
        self._prepare_joke_return()

    def _prepare_joke_return(self) -> None:
        self._destroy_joke_window()
        self._stop_current()
        self.current_clip = None
        self.finish_callback = None
        width, height = self.window.size
        self.resize_tween = {
            "started": time.monotonic(),
            "from": (width, height),
            "to": self.home_size,
            "from_center": (self.window_x + width / 2, self.window_y + height / 2),
            "to_center": self.home_center,
            "purpose": "joke_return",
        }

    def _finish_joke_return(self) -> None:
        if self.joke_close_requested:
            self.joke_close_requested = False
            self.result_pending = False
            self._start_clip("timeforyoutodie.mp4", self._begin_fly_video)
            return
        joke, self.joke_pending_text = self.joke_pending_text, None
        if joke is None:
            return
        self.joke_video_done = False
        if self.joke_executor is None:
            self.joke_executor = ThreadPoolExecutor(
                max_workers=1, thread_name_prefix="mario-joke-eval"
            )
        self.joke_future = self.joke_executor.submit(self._score_joke, joke)
        self._start_clip("joke_reaction", self._joke_reaction_finished)

    @staticmethod
    def _preload_joke_model() -> bool:
        try:
            return preload_model(ASSETS / "jokeeval.onnx")
        except Exception:
            return False

    @staticmethod
    def _score_joke(joke: str) -> int:
        model_path = ASSETS / "jokeeval.onnx"
        if not model_path.is_file():
            return 5
        try:
            return max(0, min(10, int(score_text(joke, model_path))))
        except Exception:
            return 5

    def _joke_reaction_finished(self) -> None:
        self.joke_video_done = True

    def _poll_joke_evaluation(self) -> None:
        future = self.joke_future
        if future is None or not future.done() or not self.joke_video_done:
            return
        self.joke_future = None
        try:
            rating = max(0, min(10, int(future.result())))
        except Exception:
            rating = 5
        self._begin_joke_result_transition(rating >= 6)

    def _begin_joke_result_transition(self, won: bool) -> None:
        self.joke_result_won = won
        sound_name = "kaching.wav" if won else "disappointment.wav"
        sound_path = ASSETS / sound_name
        if self.catch_sound_channel is not None and sound_path.is_file():
            try:
                self.catch_sound = pygame.mixer.Sound(str(sound_path))
                self.catch_sound_channel.play(self.catch_sound)
            except pygame.error:
                self.catch_sound = None
        self.joke_result_deadline = time.monotonic() + 0.75

    def _update_joke_result_transition(self) -> None:
        deadline = self.joke_result_deadline
        if deadline is None or time.monotonic() < deadline:
            return
        self.joke_result_deadline = None
        if self.joke_result_won:
            self._start_clip("fight_succeeded", self._play_goodbye)
        else:
            self.result_pending = False
            self._start_clip("timeforyoutodie.mp4", self._begin_fly_video)

    def _begin_fly_video(self) -> None:
        song = ASSETS / "vspatrick.mp3"
        if not song.is_file():
            raise FileNotFoundError(f"Background song not found: {song}")
        probe = shutil.which("ffprobe")
        if probe is not None:
            duration = subprocess.run(
                [probe, "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(song)],
                capture_output=True, text=True,
            )
            try:
                self.song_duration = float(duration.stdout.strip())
            except ValueError:
                self.song_duration = 0.0
        pygame.mixer.music.load(str(song))
        pygame.mixer.music.play(loops=-1)
        self.fly_pause_until = time.monotonic() + FLY_PAUSE_SECONDS

    @staticmethod
    def _back_in_out(t: float) -> float:
        c1 = 1.70158
        c2 = c1 * 1.525
        if t < 0.5:
            x = 2 * t
            return (x * x * ((c2 + 1) * x - c2)) / 2
        x = 2 * t - 2
        return (x * x * ((c2 + 1) * x + c2) + 2) / 2

    def _begin_shrink(self) -> None:
        width, height = self.window.size
        self.resize_tween = {
            "started": time.monotonic(),
            "from": (width, height),
            "to": (max(1, width // 2), max(1, height // 2)),
            "center": (self.window_x + width / 2, self.window_y + height / 2),
            "purpose": "shrink",
        }

    def _set_window_size(self, size: tuple[int, int], center: tuple[float, float]) -> None:
        size = (max(1, size[0]), max(1, size[1]))
        self.window.size = size
        self.window_x = round(center[0] - size[0] / 2)
        self.window_y = round(center[1] - size[1] / 2)
        self.window.position = (self.window_x, self.window_y)

    def _update_tween(self) -> None:
        if self.resize_tween is None:
            return
        tween = self.resize_tween
        progress = min(1.0, (time.monotonic() - tween["started"]) / TWEEN_SECONDS)
        eased = self._back_in_out(progress)
        minimum_size_reached = False
        if tween["purpose"] == "chase_reset":
            end_center_x, end_center_y = tween["to_center"]
            start_w, start_h = tween["from"]
            end_w, end_h = tween["to"]
            width = round(start_w + (end_w - start_w) * eased)
            height = round(start_h + (end_h - start_h) * eased)
            center_x = tween["from_center"][0] + (end_center_x - tween["from_center"][0]) * eased
            center_y = tween["from_center"][1] + (end_center_y - tween["from_center"][1]) * eased
            self._set_window_size((width, height), (center_x, center_y))
        elif tween["purpose"] == "return_position":
            start_x, start_y = tween["from"]
            end_x, end_y = tween["to"]
            self.window_x = start_x + (end_x - start_x) * eased
            self.window_y = start_y + (end_y - start_y) * eased
            self.window.position = (round(self.window_x), round(self.window_y))
        elif tween["purpose"] in ("joke_position", "joke_return"):
            start_w, start_h = tween["from"]
            end_w, end_h = tween["to"]
            width = round(start_w + (end_w - start_w) * eased)
            height = round(start_h + (end_h - start_h) * eased)
            start_center = tween["from_center"]
            end_center = tween["to_center"]
            center = (start_center[0] + (end_center[0] - start_center[0]) * eased,
                      start_center[1] + (end_center[1] - start_center[1]) * eased)
            self._set_window_size((width, height), center)
            self.window_x = self.window.position[0]
            self.window_y = self.window.position[1]
        else:
            start_w, start_h = tween["from"]
            end_w, end_h = tween["to"]
            size = (round(start_w + (end_w - start_w) * eased),
                    round(start_h + (end_h - start_h) * eased))
            if tuple(self.window.size) != size:
                self._set_window_size(size, tween["center"])
            if tween["purpose"] == "win_close":
                actual_size = tuple(self.window.size)
                minimum_size_reached = (
                    actual_size[0] > size[0] and actual_size[1] > size[1]
                )
        if progress >= 1.0 or minimum_size_reached:
            self.resize_tween = None
            if tween["purpose"] == "shrink":
                self._set_window_size(tween["to"], tween["center"])
                self._start_looping_fly_video()
            elif tween["purpose"] == "chase_shrink":
                self._set_window_size(tween["to"], tween["center"])
                self._begin_chase()
            elif tween["purpose"] == "return_position":
                self.window_x, self.window_y = self.home_position
                self.window.position = self.home_position
                width, height = tween["size"]
                self.resize_tween = {
                    "started": time.monotonic(),
                    "from": tuple(self.window.size),
                    "to": (width, height),
                    "center": self.home_center,
                    "purpose": "restore_size",
                }
            elif tween["purpose"] == "joke_position":
                self._set_window_size(tween["to"], tween["to_center"])
                self.window_x, self.window_y = self.window.position
                self.joke_ready = True
                self._start_clip("joke_keyboard")
            elif tween["purpose"] == "joke_return":
                self._set_window_size(self.home_size, self.home_center)
                self.window_x, self.window_y = self.home_position
                self.window.position = self.home_position
                self._finish_joke_return()
            elif tween["purpose"] == "restore_size":
                self._set_window_size(tween["to"], self.home_center)
                self._stop_current()
                self.current_clip = None
                self.finish_callback = None
                self.bouncing = False
                self.launch_ikemen = True
                self.running = False
            elif tween["purpose"] == "chase_reset":
                self._set_window_size(tween["to"], tween["to_center"])
                if tween["won"]:
                    self._start_clip("fight_succeeded", self._play_goodbye)
                else:
                    self._start_clip(
                        "fight_failed",
                        lambda: self._begin_loss_bounce(from_chase=True),
                    )
            elif tween["purpose"] == "win_close":
                self._set_window_size(tuple(self.window.size), tween["center"])
                self.result_pending = False
                self.exit_after_sound = True
                self.running = False

    def _start_looping_fly_video(self) -> None:
        self._start_clip("fly_loop", loops=-1)
        self.desktop_width, self.desktop_height = self._desktop_size()
        self.bouncing = True
        if self.loss_reaction_pending:
            self.loss_reaction_pending = False
            self.velocity_x = 3 * 650.0
            self.velocity_y = 3 * 500.0
            self.loss_bouncing = True
            self.loss_bounce_count = 0
            self.loss_speed_scale = 3.0
            self.loss_music_speed = LOSS_MUSIC_START_SPEED
            self._start_fast_music()
            self.loss_bounce_started = time.monotonic()
        else:
            self.velocity_x = 1.5 * 650.0
            self.velocity_y = 1.5 * 500.0

    def _begin_return_to_start(self) -> None:
        self.bouncing = False
        if (round(self.window_x), round(self.window_y)) == self.home_position:
            self.window_x, self.window_y = self.home_position
            if tuple(self.window.size) == self.home_size:
                self.launch_ikemen = True
                self.running = False
            else:
                self.resize_tween = {
                    "started": time.monotonic(),
                    "from": tuple(self.window.size),
                    "to": self.home_size,
                    "center": self.home_center,
                    "purpose": "restore_size",
                }
            return
        self.resize_tween = {
            "started": time.monotonic(),
            "from": (self.window_x, self.window_y),
            "to": self.home_position,
            "size": self.home_size,
            "purpose": "return_position",
        }

    def _skip_playback(self) -> None:
        """Skip active playback, or finish the fly trick if it is underway."""
        if self.loss_reaction_pending or self.loss_bouncing:
            return
        trick_active = (
            (self.current_clip in ("fly_intro", "fly_loop") and not self.video_ended)
            or self.bouncing
            or self.resize_tween is not None
        )
        if trick_active:
            if self.current_clip is not None:
                self._stop_current()
                self.current_clip = None
                self.finish_callback = None
                self.video_ended = False
            self.resize_tween = None
            self._begin_return_to_start()
            return

        if self.current_clip is None or self.video_ended:
            return
        key = self.current_clip
        callback, self.finish_callback = self.finish_callback, None
        self._stop_current()
        self.current_clip = None
        self.video_ended = False
        if key != "dontleavemeallalone.avi" and callback is not None:
            callback()

    def _show_fight_result(self, player_won: bool) -> None:
        self.critical_sound = self._load_critical_sound()
        self.result_pending = True
        if player_won:
            self._start_clip("fight_succeeded", self._begin_postfight_win)
        else:
            self._start_clip("fight_failed", self._begin_loss_bounce)

    def _begin_postfight_win(self) -> None:
        self._start_clip("ready_to_run", self._play_on_your_mark)

    def _play_on_your_mark(self) -> None:
        self._start_clip("on_your_mark", self._begin_chase_shrink)

    def _begin_chase_shrink(self) -> None:
        width, height = self.home_size
        self.resize_tween = {
            "started": time.monotonic(),
            "from": tuple(self.window.size),
            "to": (max(1, width // 3), max(1, height // 3)),
            "center": (self.window_x + width / 2, self.window_y + height / 2),
            "purpose": "chase_shrink",
        }

    def _begin_chase(self) -> None:
        if self.chase_texture_frame is None:
            frame_bytes = self._extract_chase_frame()
            self.chase_texture_frame = pygame.image.frombuffer(
                frame_bytes, VIDEO_SIZE, "RGB"
            ).copy()
        self._stop_current()
        self.current_clip = None
        self.frame = self.chase_texture_frame
        self.scaled_frame = None
        self.canvas_dirty = True
        self.desktop_width, self.desktop_height = self._desktop_size()
        self.chasing = True
        self.chase_started = time.monotonic()
        self._stop_alarm_warning()
        self.chase_escape_until = 0.0
        self.chase_positions.clear()
        self.chase_last_sample = None
        self.bouncing = False
        chase_music = ASSETS / "chase.ogg"
        pygame.mixer.music.stop()
        pygame.mixer.music.load(str(chase_music))
        pygame.mixer.music.play(loops=-1)
        self.chase_music_active = True
        self.chase_timer_value = None
        self._update_chase_timer(CHASE_SECONDS)
        fly_sound = self.sounds.get("chase_fly")
        if self.audio_channel is not None and fly_sound is not None:
            self.audio_channel.play(fly_sound, loops=-1)

    def _global_mouse_position(self) -> tuple[int, int]:
        if self.sdl is not None:
            x, y = ctypes.c_int(), ctypes.c_int()
            self.sdl.SDL_GetGlobalMouseState(ctypes.byref(x), ctypes.byref(y))
            return x.value, y.value
        local_x, local_y = pygame.mouse.get_pos()
        return round(self.window_x + local_x), round(self.window_y + local_y)

    def _update_chase_timer(self, seconds_remaining: float) -> None:
        seconds = max(0, math.ceil(seconds_remaining))
        if self.chase_timer_value == seconds:
            return
        self.chase_timer_value = seconds

        if self.chase_timer_window is None:
            self.chase_timer_window = Window(
                "Mario Head — Chase Timer", size=(1, 1), resizable=False,
                borderless=True,
            )
            self.chase_timer_renderer = Renderer(
                self.chase_timer_window, accelerated=False
            )
            self.chase_timer_tween = {
                "started": time.monotonic(),
                "from": (1, 1),
            }
            self._configure_chase_timer_window()
        self._render_chase_timer_text((255, 255, 255))

    def _render_chase_timer_text(self, color: tuple[int, int, int]) -> None:
        if self.chase_timer_renderer is None or self.chase_timer_value is None:
            return
        text = self.chase_timer_font.render(str(self.chase_timer_value), True, color)
        padding = 12
        size = (text.get_width() + padding * 2, text.get_height() + padding * 2)
        surface = pygame.Surface(size)
        surface.fill((24, 24, 24))
        surface.blit(text, (padding, padding))
        self.chase_timer_target_size = size
        self.chase_timer_texture = Texture(
            self.chase_timer_renderer, size, streaming=True
        )
        self.chase_timer_texture.update(surface)
        self.chase_timer_color = color
        self.chase_timer_dirty = True

    def _set_window_always_on_top(self, window: Window, enabled: bool) -> None:
        if self.sdl is not None:
            try:
                get_window = self.sdl.SDL_GetWindowFromID
                get_window.argtypes = [ctypes.c_uint32]
                get_window.restype = ctypes.c_void_p
                native_window = get_window(window.id)
                set_top = self.sdl.SDL_SetWindowAlwaysOnTop
                set_top.argtypes = [ctypes.c_void_p, ctypes.c_int]
                set_top.restype = None
                set_top(native_window, int(enabled))
                return
            except (AttributeError, OSError):
                pass
        try:
            window.always_on_top = enabled
        except AttributeError:
            pass

    def _configure_chase_timer_window(self) -> None:
        window = self.chase_timer_window
        if window is None:
            return
        native_window = None
        self._set_window_always_on_top(window, True)
        if self.sdl is not None:
            try:
                get_window = self.sdl.SDL_GetWindowFromID
                get_window.argtypes = [ctypes.c_uint32]
                get_window.restype = ctypes.c_void_p
                native_window = get_window(window.id)
            except (AttributeError, OSError):
                native_window = None
        if self.sdl is not None:
            try:
                class SDLVersion(ctypes.Structure):
                    _fields_ = [("major", ctypes.c_uint8),
                                ("minor", ctypes.c_uint8),
                                ("patch", ctypes.c_uint8)]

                class X11Info(ctypes.Structure):
                    _fields_ = [("display", ctypes.c_void_p),
                                ("window", ctypes.c_ulong)]

                class SysWMUnion(ctypes.Union):
                    _fields_ = [("x11", X11Info),
                                ("padding", ctypes.c_uint8 * 64)]

                class SysWMInfo(ctypes.Structure):
                    _fields_ = [("version", SDLVersion),
                                ("subsystem", ctypes.c_int),
                                ("info", SysWMUnion)]

                wm_info = SysWMInfo()
                wm_info.version = SDLVersion(2, 0, 0)
                get_info = self.sdl.SDL_GetWindowWMInfo
                get_info.argtypes = [ctypes.c_void_p, ctypes.POINTER(SysWMInfo)]
                get_info.restype = ctypes.c_int
                if (native_window and get_info(native_window, ctypes.byref(wm_info))
                        and wm_info.subsystem == 2):
                    fixes_path = ctypes.util.find_library("Xfixes")
                    if fixes_path:
                        fixes = ctypes.CDLL(fixes_path)
                        fixes.XFixesCreateRegion.argtypes = [
                            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int
                        ]
                        fixes.XFixesCreateRegion.restype = ctypes.c_void_p
                        fixes.XFixesSetWindowShapeRegion.argtypes = [
                            ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int,
                            ctypes.c_int, ctypes.c_int, ctypes.c_void_p,
                        ]
                        fixes.XFixesSetWindowShapeRegion.restype = None
                        region = fixes.XFixesCreateRegion(wm_info.info.x11.display,
                                                          None, 0)
                        fixes.XFixesSetWindowShapeRegion(
                            wm_info.info.x11.display, wm_info.info.x11.window,
                            2, 0, 0, region,
                        )
                        flush = ctypes.CDLL(ctypes.util.find_library("X11"))
                        flush.XFlush.argtypes = [ctypes.c_void_p]
                        flush.XFlush(wm_info.info.x11.display)
                        fixes.XFixesDestroyRegion.argtypes = [ctypes.c_void_p,
                                                             ctypes.c_void_p]
                        fixes.XFixesDestroyRegion(wm_info.info.x11.display, region)
                    try:
                        self.window.focus(input_only=True)
                    except pygame.error:
                        pass
            except (AttributeError, OSError, ValueError):
                pass

    def _update_chase_timer_tween(self, seconds_remaining: float | None) -> None:
        if self.chase_timer_window is None or self.chase_timer_renderer is None:
            return
        if self.chase_timer_dismiss_tween is not None:
            tween = self.chase_timer_dismiss_tween
            progress = min(1.0, (time.monotonic() - tween["started"]) / TWEEN_SECONDS)
            eased = self._back_in_out(progress)
            start_width, start_height = tween["from"]
            size = (max(1, round(start_width * (1.0 - eased))),
                    max(1, round(start_height * (1.0 - eased))))
            if tuple(self.chase_timer_window.size) != size:
                self.chase_timer_window.size = size
                self.chase_timer_dirty = True
            actual_size = tuple(self.chase_timer_window.size)
            position = (max(0, (self.desktop_width - actual_size[0]) // 2), 0)
            if tuple(self.chase_timer_window.position) != position:
                self.chase_timer_window.position = position
                self.chase_timer_dirty = True
            if self.chase_timer_texture is not None:
                if self.chase_timer_dirty:
                    self.chase_timer_renderer.draw_color = (24, 24, 24, 255)
                    self.chase_timer_renderer.clear()
                    self.chase_timer_texture.draw(dstrect=(0, 0, *actual_size))
                    self.chase_timer_renderer.present()
                    self.chase_timer_dirty = False
            if progress >= 1.0:
                self._destroy_chase_timer()
            return

        warning = seconds_remaining is not None and seconds_remaining <= 10
        if warning:
            self._start_alarm_warning()
            flash = int((time.monotonic() - self.chase_started) * 4) % 2
            color = (255, 40, 40) if flash == 0 else (255, 255, 255)
            if self.chase_timer_color != color:
                self._render_chase_timer_text(color)

        base_width, base_height = self.chase_timer_target_size or (1, 1)
        pulse = 1.0
        if warning:
            elapsed = time.monotonic() - self.chase_started
            pulse = 1.0 + 0.16 * math.sin(elapsed * math.tau * 3)
        target_size = (max(1, round(base_width * pulse)),
                       max(1, round(base_height * pulse)))
        if self.chase_timer_tween is not None:
            tween = self.chase_timer_tween
            progress = min(1.0, (time.monotonic() - tween["started"]) / TWEEN_SECONDS)
            eased = self._back_in_out(progress)
            start_width, start_height = tween["from"]
            target_width, target_height = target_size
            size = (
                max(1, round(start_width + (target_width - start_width) * eased)),
                max(1, round(start_height + (target_height - start_height) * eased)),
            )
            if tuple(self.chase_timer_window.size) != size:
                self.chase_timer_window.size = size
                self.chase_timer_dirty = True
            if progress >= 1.0:
                if tuple(self.chase_timer_window.size) != target_size:
                    self.chase_timer_window.size = target_size
                    self.chase_timer_dirty = True
                self.chase_timer_tween = None
        else:
            if tuple(self.chase_timer_window.size) != target_size:
                self.chase_timer_window.size = target_size
                self.chase_timer_dirty = True

        actual_size = tuple(self.chase_timer_window.size)
        position = (max(0, (self.desktop_width - actual_size[0]) // 2), 0)
        if tuple(self.chase_timer_window.position) != position:
            self.chase_timer_window.position = position
            self.chase_timer_dirty = True
        if self.chase_timer_texture is not None and self.chase_timer_dirty:
            self.chase_timer_renderer.draw_color = (24, 24, 24, 255)
            self.chase_timer_renderer.clear()
            self.chase_timer_texture.draw(dstrect=(0, 0, *actual_size))
            self.chase_timer_renderer.present()
            self.chase_timer_dirty = False

    def _destroy_chase_timer(self) -> None:
        if self.chase_timer_window is not None:
            self.chase_timer_texture = None
            self.chase_timer_renderer = None
            self.chase_timer_window.destroy()
            self.chase_timer_window = None
        self.chase_timer_value = None
        self.chase_timer_target_size = None
        self.chase_timer_tween = None
        self.chase_timer_dismiss_tween = None
        self.chase_timer_color = None
        self.chase_timer_dirty = False
        self._stop_alarm_warning()

    def _shrink_chase_timer(self) -> None:
        if self.chase_timer_window is None or self.chase_timer_dismiss_tween is not None:
            return
        self._stop_alarm_warning()
        self.chase_timer_dismiss_tween = {
            "started": time.monotonic(),
            "from": tuple(self.chase_timer_window.size),
        }

    def _start_alarm_warning(self) -> None:
        if self.alarm_active or self.alarm_channel is None:
            return
        alarm_path = ASSETS / "alarm.wav"
        if not alarm_path.is_file():
            return
        try:
            if self.alarm_sound is None:
                self.alarm_sound = pygame.mixer.Sound(str(alarm_path))
            self.alarm_channel.play(self.alarm_sound, loops=-1)
            self.alarm_active = True
        except pygame.error:
            self.alarm_sound = None

    def _stop_alarm_warning(self) -> None:
        if self.alarm_channel is not None:
            self.alarm_channel.stop()
        self.alarm_active = False

    def _record_chase_position(self) -> None:
        """Detect five repeated back-and-forth trips between two screen points."""
        point = (round(self.window_x / 32), round(self.window_y / 32))
        if (self.chase_last_sample is None
                or math.dist(point, self.chase_last_sample) >= 2):
            self.chase_positions.append(point)
            self.chase_last_sample = point

        history = self.chase_positions
        if len(history) < history.maxlen:
            return
        first, second = history[0], history[1]
        if first == second:
            return
        if not all(point == (first if index % 2 == 0 else second)
                   for index, point in enumerate(history)):
            return

        toward_a = (first[0] - second[0], first[1] - second[1])
        headings = [
            (dx, dy)
            for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1),
                           (0, 1), (1, -1), (1, 0), (1, 1))
            if dx * toward_a[0] + dy * toward_a[1] <= 0
        ]
        if headings:
            dx, dy = self.chase_entropy.choice(headings)
            magnitude = math.hypot(dx, dy)
            self.chase_escape_velocity = (
                dx / magnitude * CHASE_SPEED,
                dy / magnitude * CHASE_SPEED,
            )
            self.chase_escape_until = time.monotonic() + 0.5
        history.clear()
        self.chase_last_sample = None

    def _update_chase(self, delta_seconds: float) -> None:
        if not self.chasing:
            return
        remaining = CHASE_SECONDS - (time.monotonic() - self.chase_started)
        self._update_chase_timer(remaining)
        self._update_chase_timer_tween(remaining)
        if remaining <= 10:
            self._start_alarm_warning()
        if remaining <= 0:
            self.chasing = False
            self._stop_chase_audio()
            self._shrink_chase_timer()
            self._begin_chase_result(False)
            return

        if time.monotonic() < self.chase_escape_until:
            velocity_x, velocity_y = self.chase_escape_velocity
            width, height = self.window.size
            max_x = max(0, self.desktop_width - width)
            max_y = max(0, self.desktop_height - height)
            self.window_x = min(max(0.0, self.window_x + velocity_x * delta_seconds),
                                float(max_x))
            self.window_y = min(max(0.0, self.window_y + velocity_y * delta_seconds),
                                float(max_y))
            self.window.position = (round(self.window_x), round(self.window_y))
            self._record_chase_position()
            return

        mouse_x, mouse_y = self._global_mouse_position()
        width, height = self.window.size
        center_x = self.window_x + width / 2
        center_y = self.window_y + height / 2
        away_x, away_y = center_x - mouse_x, center_y - mouse_y
        distance = math.hypot(away_x, away_y)
        if distance < 1:
            away_x, away_y, distance = 1.0, 0.0, 1.0
        max_x = max(0, self.desktop_width - width)
        max_y = max(0, self.desktop_height - height)
        if (self.window_x <= 0 and away_x < 0) or (
                self.window_x >= max_x and away_x > 0):
            away_x = 0.0
        if (self.window_y <= 0 and away_y < 0) or (
                self.window_y >= max_y and away_y > 0):
            away_y = 0.0
        distance = math.hypot(away_x, away_y)
        if distance == 0:
            at_left = self.window_x <= 0
            at_right = self.window_x >= max_x
            at_top = self.window_y <= 0
            at_bottom = self.window_y >= max_y
            headings = [
                (dx, dy)
                for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1),
                               (0, 1), (1, -1), (1, 0), (1, 1))
                if not (at_left and dx < 0)
                and not (at_right and dx > 0)
                and not (at_top and dy < 0)
                and not (at_bottom and dy > 0)
            ]
            if not headings:
                return
            away_x, away_y = self.chase_entropy.choice(headings)
            distance = math.hypot(away_x, away_y)
            self.chase_escape_velocity = (
                away_x / distance * CHASE_SPEED,
                away_y / distance * CHASE_SPEED,
            )
            self.chase_escape_until = time.monotonic() + 0.45
            velocity_x, velocity_y = self.chase_escape_velocity
        else:
            velocity_x = away_x / distance * CHASE_SPEED
            velocity_y = away_y / distance * CHASE_SPEED
        self.window_x += velocity_x * delta_seconds
        self.window_y += velocity_y * delta_seconds
        self.window_x = min(max(0.0, self.window_x), float(max_x))
        self.window_y = min(max(0.0, self.window_y), float(max_y))
        self.window.position = (round(self.window_x), round(self.window_y))
        self._record_chase_position()

    def _stop_chase_audio(self) -> None:
        if self.audio_channel is not None:
            self.audio_channel.stop()
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        self.chase_music_active = False

    def _catch_mario(self) -> None:
        if not self.chasing:
            return
        self.chasing = False
        self._stop_chase_audio()
        self._shrink_chase_timer()
        self._begin_chase_result(True)

    def _begin_chase_result(self, won: bool) -> None:
        """Center Mario and restore his original size before either result plays."""
        self.bouncing = False
        result_sound = ASSETS / ("kaching.wav" if won else "disappointment.wav")
        if self.catch_sound_channel is not None and result_sound.is_file():
            try:
                self.catch_sound = pygame.mixer.Sound(str(result_sound))
                self.catch_sound_channel.play(self.catch_sound)
            except pygame.error:
                self.catch_sound = None
        self.desktop_width, self.desktop_height = self._desktop_size()
        width, height = self.window.size
        start_center = (self.window_x + width / 2, self.window_y + height / 2)
        target_center = (self.desktop_width / 2, self.desktop_height / 2)
        self.resize_tween = {
            "started": time.monotonic(),
            "from": (width, height),
            "to": self.home_size,
            "from_position": (self.window_x, self.window_y),
            "from_center": start_center,
            "to_center": target_center,
            "won": won,
            "purpose": "chase_reset",
        }

    def _play_goodbye(self) -> None:
        self._start_clip("goodbye", self._finish_goodbye)

    def _finish_goodbye(self) -> None:
        width, height = self.window.size
        self.resize_tween = {
            "started": time.monotonic(),
            "from": (width, height),
            "to": (1, 1),
            "center": (self.window_x + width / 2, self.window_y + height / 2),
            "purpose": "win_close",
        }

    def _play_information_sound_after_shutdown(self) -> None:
        if sys.platform == "win32":
            try:
                import winsound

                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            except (ImportError, RuntimeError):
                try:
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                except (NameError, RuntimeError):
                    pass
            return

        platform_key = "darwin" if sys.platform == "darwin" else "linux"
        candidates = INFO_SOUND_CANDIDATES.get(platform_key, ())
        sound_path = next((path for path in candidates if path.is_file()), None)
        if sound_path is None:
            if sys.platform == "darwin":
                osascript = shutil.which("osascript")
                if osascript is not None:
                    subprocess.run(
                        [osascript, "-e", "beep 1"],
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=False,
                    )
            return
        if sys.platform == "darwin":
            player = shutil.which("afplay")
            if player is None:
                return
            command = [player, str(sound_path)]
        else:
            player = shutil.which("ffplay")
            if player is not None:
                command = [player, "-nodisp", "-autoexit", "-loglevel", "quiet", str(sound_path)]
            else:
                player = shutil.which("paplay")
                if player is None:
                    return
                command = [player, str(sound_path)]
        subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )

    def _play_exit_sound_after_close(self) -> None:
        self.close()
        self._play_information_sound_after_shutdown()

    def _begin_loss_bounce(self, from_chase: bool = False) -> None:
        self.result_pending = False
        if not from_chase:
            self._set_window_size(self.home_size, self.home_center)
            self.window_x, self.window_y = self.home_position
            self.window.position = self.home_position
        self.velocity_x = 650.0
        self.velocity_y = 500.0
        self.loss_bouncing = False
        self.bouncing = False
        self.loss_reaction_pending = True
        self._begin_shrink()

    def _start_fast_music(self) -> None:
        """Start the looping song at the current rate, with pitch following rate."""
        song = ASSETS / "vspatrick.mp3"
        if not song.is_file():
            return
        pygame.mixer.music.stop()
        try:
            self.loss_music = RateControlledMusic(
                self.ffmpeg, song, self.song_position_at_fight
            )
            self.loss_music.play(LOSS_MUSIC_START_SPEED)
        except Exception as exc:
            self.loss_music = None
            print(f"Mario Head rate-controlled music unavailable: {exc}", file=sys.stderr)
            self._fallback_loss_music()
    def _fallback_loss_music(self) -> None:
        song = ASSETS / "vspatrick.mp3"
        try:
            pygame.mixer.music.load(str(song))
            pygame.mixer.music.play(
                loops=-1, start=self.song_position_at_fight
            )
        except pygame.error:
            pygame.mixer.music.load(str(song))
            pygame.mixer.music.play(loops=-1)

    def _update_loss_bounce(self) -> None:
        if not self.loss_bouncing:
            return
        if time.monotonic() - self.loss_bounce_started >= LOSS_BOUNCE_SECONDS:
            self.loss_bouncing = False
            self.bouncing = False
            self.running = False

    def _max_loss_speed_scale(self) -> float:
        width, height = self.window.size
        span_x = max(1, self.desktop_width - width)
        span_y = max(1, self.desktop_height - height)
        max_x_speed = span_x * RENDER_FPS / BOUNCE_CROSSING_FRAMES
        max_y_speed = span_y * RENDER_FPS / BOUNCE_CROSSING_FRAMES
        return max(3.0, min(max_x_speed / 650.0, max_y_speed / 500.0))

    @staticmethod
    def _advance_axis(position: float, velocity: float, delta: float,
                      limit: int) -> tuple[float, float, int]:
        """Advance and reflect across any number of borders without clamping jumps."""
        if limit <= 0:
            return 0.0, velocity, 0
        unfolded = position if velocity >= 0 else 2 * limit - position
        end = unfolded + abs(velocity) * delta
        crossed = max(
            0,
            math.floor(end / limit + 1e-12)
            - math.floor(unfolded / limit + 1e-12),
        )
        phase = end % (2 * limit)
        if phase < limit:
            return phase, abs(velocity), crossed
        return 2 * limit - phase, -abs(velocity), crossed

    def _update_bounce(self, delta_seconds: float) -> None:
        if not self.bouncing or self.resize_tween is not None:
            return
        width, height = self.window.size
        max_x = max(0, self.desktop_width - width)
        max_y = max(0, self.desktop_height - height)
        self.window_x, self.velocity_x, hits_x = self._advance_axis(
            self.window_x, self.velocity_x, delta_seconds, max_x
        )
        self.window_y, self.velocity_y, hits_y = self._advance_axis(
            self.window_y, self.velocity_y, delta_seconds, max_y
        )
        bounce_hits = hits_x + hits_y
        if bounce_hits:
            self._play_critical_sound()
        if bounce_hits:
            if self.loss_bouncing:
                self.loss_bounce_count += bounce_hits
                max_scale = self._max_loss_speed_scale()
                hits_to_cap = math.log(max_scale / self.loss_speed_scale) / math.log(1.25)
                if bounce_hits >= hits_to_cap:
                    self.loss_speed_scale = max_scale
                else:
                    self.loss_speed_scale *= 1.25 ** bounce_hits
                self.velocity_x = math.copysign(650.0 * self.loss_speed_scale, self.velocity_x)
                self.velocity_y = math.copysign(500.0 * self.loss_speed_scale, self.velocity_y)
                self.loss_music_speed = (
                    LOSS_MUSIC_START_SPEED * self.loss_speed_scale / 3.0
                )
                if self.loss_music is not None:
                    self.loss_music.set_rate(self.loss_music_speed)
            else:
                self.bounce_count += bounce_hits
                if self.bounce_count >= BORDER_BOUNCES_BEFORE_FIGHT:
                    self._begin_return_to_start()
        self.window.position = (round(self.window_x), round(self.window_y))

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if not self.result_pending:
                    self.running = False
            elif event.type == pygame.KEYDOWN:
                is_star = (
                    event.key == pygame.K_KP_MULTIPLY
                    or getattr(event, "unicode", "") == "*"
                    or (event.key == pygame.K_8 and event.mod & pygame.KMOD_SHIFT)
                )
                is_minus = (
                    event.key in (pygame.K_MINUS, pygame.K_KP_MINUS)
                    or getattr(event, "unicode", "") == "-"
                )
                if is_star:
                    self.skip_star_down = True
                if is_minus:
                    self.skip_minus_down = True
                if (self.skip_star_down and self.skip_minus_down
                        and not self.skip_chord_latched):
                    self.skip_chord_latched = True
                    self._skip_playback()
                if self.question_open:
                    if event.key in (pygame.K_y, pygame.K_RETURN):
                        self._answer(True)
                    elif event.key in (pygame.K_n, pygame.K_ESCAPE):
                        self._answer(False)
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_8, pygame.K_KP_MULTIPLY):
                    self.skip_star_down = False
                if event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.skip_minus_down = False
                if not (self.skip_star_down and self.skip_minus_down):
                    self.skip_chord_latched = False
            elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                  and self.chasing):
                self._catch_mario()

    def _advance_video(self) -> None:
        if self.current_decoder is None or self.video_ended or self.frame_queue is None:
            return
        now = time.monotonic()
        elapsed = now - self.clip_started_at
        target_frames = max(1, int(elapsed * VIDEO_FPS) + 1)
        target_frames = max(target_frames, self.video_frames_consumed)

        while self.video_frames_consumed < target_frames:
            try:
                data = self.frame_queue.get_nowait()
            except queue.Empty:
                return
            if data is None:
                self.video_ended = True
                process, self.current_decoder = self.current_decoder, None
                if process.stdout is not None:
                    process.stdout.close()
                process.wait()
                return
            self.frame = pygame.image.frombuffer(data, VIDEO_SIZE, "RGB").copy()
            self.scaled_frame = None
            self.canvas_dirty = True
            self.video_frames_consumed += 1

    def _finish_clip_if_ready(self) -> None:
        if not self.video_ended:
            return
        if self.audio_channel is not None and self.audio_channel.get_busy():
            return
        callback, self.finish_callback = self.finish_callback, None
        self.current_clip = None
        if callback:
            callback()

    def _draw_frame(self) -> None:
        if self.frame is None:
            return
        size = self.canvas.get_size()
        if self.scaled_frame is None or self.scaled_frame_size != size:
            self.scaled_frame = pygame.transform.smoothscale(self.frame, size)
            self.scaled_frame_size = size
        self.canvas.blit(self.scaled_frame, (0, 0))

    def run(self) -> None:
        try:
            while self.running:
                delta_seconds = self.clock.tick(RENDER_FPS) / 1000
                self._handle_events()
                self._pump_qt_events()
                self._update_tween()
                self._update_loss_bounce()
                self._update_chase(delta_seconds)
                if not self.chasing and self.chase_timer_window is not None:
                    self._update_chase_timer_tween(None)
                self._update_bounce(delta_seconds)
                if hasattr(self, "fly_pause_until") and self.current_clip is None:
                    if time.monotonic() >= self.fly_pause_until:
                        del self.fly_pause_until
                        self._start_clip("fly_intro", self._begin_shrink)
                if self.question_open and not self.wait_clip_started:
                    if time.monotonic() - self.question_started >= 10:
                        self.wait_clip_started = True
                        self._start_clip("dontleavemeallalone.avi")
                self._advance_video()
                self._finish_clip_if_ready()
                self._poll_joke_evaluation()
                self._update_joke_result_transition()

                if self.canvas_dirty:
                    self.canvas.fill((0, 0, 0))
                    self._draw_frame()
                self._present()
        finally:
            if not self.launch_ikemen:
                self.close()

    def _wait_for_fight(self, command: list[str], log_path: Path) -> bool:
        """Run IKEMEN and read its recorded winning side; unknown results are losses."""
        self.running = True
        elapsed_ms = pygame.mixer.music.get_pos()
        if elapsed_ms >= 0:
            self.song_position_at_fight = elapsed_ms / 1000
            if self.song_duration > 0:
                self.song_position_at_fight %= self.song_duration
        pygame.mixer.music.pause()
        self._set_window_always_on_top(self.window, False)
        try:
            self.window.show()
            if sys.platform.startswith("linux"):
                try:
                    Path("/proc/self/oom_score_adj").write_text("-1000")
                except OSError:
                    pass
                launcher = (
                    'echo 1000 > /proc/self/oom_score_adj 2>/dev/null || true; '
                    'exec "$@"'
                )
                fight = subprocess.Popen(
                    ["/bin/sh", "-c", launcher, "mario-ikemen", *command],
                    cwd=IKEMEN_DIR,
                    stdin=subprocess.DEVNULL,
                )
                try:
                    Path(f"/proc/{fight.pid}/oom_score_adj").write_text("1000")
                except OSError:
                    pass
            else:
                fight = subprocess.Popen(
                    command, cwd=IKEMEN_DIR, stdin=subprocess.DEVNULL
                )
            while fight.poll() is None:
                pygame.event.get()
                time.sleep(0.15)
            fight.wait()
            self._set_window_always_on_top(self.window, True)
            try:
                report = log_path.read_text(errors="replace") if log_path.is_file() else ""
            except OSError:
                report = ""
            winner_values = re.findall(
                r'\[?\s*["\']?(?:MarioWinnerSide|WinSide)["\']?\s*\]?'
                r'\s*(?:=>|=|:)\s*(-?\d+)',
                report,
                flags=re.IGNORECASE,
            )
            winning_side = int(winner_values[-1]) if winner_values else None
            return winning_side == 1
        finally:
            self._set_window_always_on_top(self.window, True)
            try:
                log_path.unlink(missing_ok=True)
            except OSError:
                pass

    def idle_after_fight(self) -> None:
        """Run the judgement clip, then remain idle or complete the loss reaction."""
        while self.running:
            delta_seconds = self.clock.tick(RENDER_FPS) / 1000
            self._handle_events()
            self._pump_qt_events()
            self._update_tween()
            self._update_loss_bounce()
            self._update_chase(delta_seconds)
            if not self.chasing and self.chase_timer_window is not None:
                self._update_chase_timer_tween(None)
            self._update_bounce(delta_seconds)
            self._advance_video()
            self._finish_clip_if_ready()
            self._poll_joke_evaluation()
            self._update_joke_result_transition()
            if self.canvas_dirty:
                self.canvas.fill((0, 0, 0))
                self._draw_frame()
            self._present()
        self.close()

    def close(self) -> None:
        if self.resources_closed:
            return
        self.resources_closed = True
        self._destroy_joke_window()
        if self.joke_executor is not None:
            self.joke_executor.shutdown(wait=False, cancel_futures=True)
            self.joke_executor = None
        self._destroy_chase_timer()
        if self.catch_sound_channel is not None:
            self.catch_sound_channel.stop()
        self._stop_alarm_warning()
        if self.question_window is not None:
            try:
                self.question_window.destroy()
            except self.question_tk.TclError:
                pass
            self.question_window = None
        if self.question_root is not None:
            try:
                self.question_root.destroy()
            except self.question_tk.TclError:
                pass
            self.question_root = None
        self._stop_current()
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        if self.loss_music is not None:
            self.loss_music.close()
            self.loss_music = None
        for process in self.decoders.values():
            if process.poll() is None:
                process.terminate()
            if process.stdout is not None:
                process.stdout.close()
            process.wait()
        self.decoders.clear()
        self.temp_dir.cleanup()
        self.sounds.clear()
        self.catch_sound = None
        self.alarm_sound = None
        self.critical_sound = None
        self.chase_texture_frame = None
        self.frame = None
        self.scaled_frame = None
        self.audio_channel = None
        self.catch_sound_channel = None
        self.alarm_channel = None
        self.canvas_texture = None
        self.renderer = None
        self.canvas = None
        self.window.destroy()
        pygame.quit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Mario Head")
    parser.add_argument("--skipto", choices=("lose", "win"),
                        help="skip the intro and go straight to the lose or win sequence")
    args = parser.parse_args()
    restore_terminal = _install_terminal_restore()
    app = None
    try:
        app = MarioHead(skip_to=args.skipto)
        app.run()
        if app.exit_after_sound:
            app._play_exit_sound_after_close()
            return
        if app.launch_ikemen:
            executable = ikemen_executable()
            p1 = "roa Marvin/roa Marvin.def"
            p2 = "Mario Head/Mario Head.def"
            p3 = "SBobSPants/SBobSPants.def"
            if not executable.is_file():
                raise FileNotFoundError(f"IKEMEN GO executable not found: {executable}")
            with tempfile.NamedTemporaryFile(
                prefix="mario-ikemen-result-", suffix=".log", delete=False
            ) as result_file:
                result_log = Path(result_file.name)
            command = [
                str(executable),
                "-p1", p1, "-p2", p2, "-p3", p3,
                "-tmode1", "1", "-tmode2", "0",
                "-p2.ai", "8", "-p3.ai", "8",
                "-rounds", "1",
                "-log", str(result_log),
            ]
            player_won = app._wait_for_fight(command, result_log)
            app._show_fight_result(player_won)
            if app.running:
                app.idle_after_fight()
            else:
                app.close()
            if app.exit_after_sound:
                app._play_information_sound_after_shutdown()
    except Exception as exc:
        if app is not None:
            app.close()
        else:
            pygame.quit()
        print(f"Mario Head: {exc}", file=sys.stderr)
        raise
    finally:
        if restore_terminal is not None:
            restore_terminal()


if __name__ == "__main__":
    main()
