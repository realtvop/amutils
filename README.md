# amutils

Command-line utilities for Apple Music library management and statistics.

## Installation

Clone the repository and ensure you have Python installed.

```bash
pip3 install --user amutils
```

## Usage

```bash
amutils <command> [file]
```

## Commands

- `stat` - Get your library statistics
- `playedtime` - Get library total played time
- `replace` - Replace songs in your library with given music file(s)

## Examples

```bash
# Get library statistics
amutils stat

# Get total played time
amutils playedtime

# Replace a single song
amutils replace path/to/song.m4a

# Replace multiple songs in a folder
amutils replace path/to/folder
```

## Features

- Library statistics tracking
- Total playtime calculation
- Smart song replacement based on metadata matching
- Support for both single file and folder processing
- Automatic metadata comparison and matching

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.