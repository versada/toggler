from io import FileIO
import pathlib

Stream = str | bytes | FileIO
OptionalStream = Stream | None
Streams = list[Stream]
OptionalStreams = Streams | None
Path = str | pathlib.Path
OptionalPath = Path | None
Paths = list[Path]
OptionalPaths = Paths | None
