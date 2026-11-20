"""Play local audio faster while preserving pitch."""

from pathlib import Path
import sys


def main(path):
    # Use the system GStreamer bindings for pitch-preserving playback.
    try:
        import gi

        gi.require_version("Gst", "1.0")
        from gi.repository import Gst
    except (ImportError, ValueError) as error:
        raise RuntimeError("Instale o PyGObject e os bindings do GStreamer para Python 3.") from error

    Gst.init(None)
    player = Gst.ElementFactory.make("playbin")
    tempo = Gst.ElementFactory.make("scaletempo")
    if player is None or tempo is None:
        raise RuntimeError("Instale os plugins base e good do GStreamer.")
    player.set_property("uri", Path(path).resolve().as_uri())
    player.set_property("audio-filter", tempo)

    # Preroll the file before setting playback to 1.5×.
    try:
        player.set_state(Gst.State.PAUSED)
        state, _, _ = player.get_state(10 * Gst.SECOND)
        if state != Gst.StateChangeReturn.SUCCESS:
            raise RuntimeError("Falha ao preparar a reprodução.")
        if not player.seek(
            1.5, Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE,
            Gst.SeekType.SET, 0, Gst.SeekType.NONE, -1,
        ):
            raise RuntimeError("Falha ao ajustar a velocidade.")
        player.set_state(Gst.State.PLAYING)
        event = player.get_bus().timed_pop_filtered(
            Gst.CLOCK_TIME_NONE, Gst.MessageType.EOS | Gst.MessageType.ERROR
        )
        if event.type == Gst.MessageType.ERROR:
            error, _ = event.parse_error()
            raise RuntimeError(error.message)
    finally:
        player.set_state(Gst.State.NULL)


if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except RuntimeError as error:
        sys.exit(f"Falha ao tocar o áudio: {error}")
