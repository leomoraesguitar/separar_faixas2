import argparse

import io
from pathlib import Path
import select
from shutil import rmtree
import subprocess as sp
import sys
import os
from typing import Dict, Tuple, Optional, IO

from google.colab import files

#@title #Funções








def find_files(in_path):
    out = []
    extensions = ["mp3", "wav", "ogg", "flac", "webm", "mp4"]
    for file in Path(in_path).iterdir():
        if file.suffix.lower().lstrip(".") in extensions:
            out.append(file)
    return out

def copy_process_streams(process: sp.Popen):
  def raw(stream: Optional[IO[bytes]]) -> IO[bytes]:
      assert stream is not None
      if isinstance(stream, io.BufferedIOBase):
          stream = stream.raw
      return stream

  p_stdout, p_stderr = raw(process.stdout), raw(process.stderr)
  stream_by_fd: Dict[int, Tuple[IO[bytes], io.StringIO, IO[str]]] = {
      p_stdout.fileno(): (p_stdout, sys.stdout),
      p_stderr.fileno(): (p_stderr, sys.stderr),
  }
  fds = list(stream_by_fd.keys())

  while fds:
    ready, _, _ = select.select(fds, [], [])
    for fd in ready:
        p_stream, std = stream_by_fd[fd]
        raw_buf = p_stream.read(2 ** 16)
        if not raw_buf:
            fds.remove(fd)
            continue
        buf = raw_buf.decode()
        std.write(buf)
        std.flush()

def separate(inp=None, outp=None):
    in_path = '/content'

    out_path = '/content/separados'  
    if not os.path.exists(in_path):
    os.makedirs(in_path)
    if not os.path.exists(out_path):
    os.makedirs(out_path)


    inp = inp or in_path
    outp = outp or out_path
    model = "htdemucs_ft" # param ["htdemucs", "htdemucs_ft", "htdemucs_6s", "hdemucs_mmi", "mdx", "mdx_extra", "mdx_q", "SIG"]
    mp3_rate = 320
    files = [str(f) for f in find_files(inp)]
    if not files:
        print(f"No valid audio files in {in_path}")
        return

    cmd = ["python3", "-m", "demucs.separate", "-o", str(outp), "-n", model]

    cmd += ["--mp3", f"--mp3-bitrate={mp3_rate}"]




    print("Going to separate the files:")
    print('\n'.join(files))
    print("With command: ", " ".join(cmd))
    input('asdalkjdlaj')
    p = sp.Popen(cmd + files, stdout=sp.PIPE, stderr=sp.PIPE)
    copy_process_streams(p)
    p.wait()
    if p.returncode != 0:
        print("Command failed, something went wrong.")







def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--separar', choices=['separate'])
    # parser.add_argument('--separar', choices=['separate'])

    args = parser.parse_args()

    if args.acao == 'separate':
        separate()
   

if __name__ == "__main__":
    # print('Para executar, faça: python comandopythonlinha.py --acao [acao1, acao2]')
    main()


