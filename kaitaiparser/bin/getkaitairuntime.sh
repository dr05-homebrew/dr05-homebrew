DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" #http://stackoverflow.com/questions/59895/can-a-bash-script-tell-which-directory-it-is-stored-in
wget -O "$DIR/../kaitaistruct.py" 'https://raw.githubusercontent.com/kaitai-io/kaitai_struct_python_runtime/master/kaitaistruct/kaitaistruct.py'
