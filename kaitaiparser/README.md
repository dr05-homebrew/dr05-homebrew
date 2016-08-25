First get enum34 for python 2, it is required by Kaitai.
Then get the kaitaistruct compiler. ( http://kaitai.io/#download )
Then get the kaitai python 2 runtime library by running getkaitairuntime.sh (downloads file from github, method may break later)
Then generate the parser with gen.sh PATH_TO_KAITAI_COMPILER

Use tmuxinator with watcher.sh (see example file in misc) to watch multiple firmware files as you edit and recompile the ksy.
